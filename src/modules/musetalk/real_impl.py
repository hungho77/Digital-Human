###############################################################################
# MuseTalk real model - relocated implementation from musereal.py
###############################################################################

import math
import torch
import numpy as np

import subprocess
import os
import time
import torch.nn.functional as F
import cv2
import glob
import pickle
import copy

import queue
from queue import Queue
from threading import Thread, Event
import torch.multiprocessing as mp

from src.modules.musetalk.utils.utils import get_file_type, get_video_fps, datagen, load_all_model
from src.modules.musetalk.myutil import get_image_blending
from src.modules.musetalk.whisper.audio2feature import Audio2Feature

from src.modules.musetalk.asr import MuseASR
import asyncio
from av import AudioFrame, VideoFrame
from src.core.base_real import BaseReal

from tqdm import tqdm
from src.utils.logger import logger


def load_model():
    # load model weights
    vae, unet, pe = load_all_model()
    device = torch.device("cuda" if torch.cuda.is_available() else ("mps" if (hasattr(torch.backends, "mps") and torch.backends.mps.is_available()) else "cpu"))
    timesteps = torch.tensor([0], device=device)
    pe = pe.half().to(device)
    vae.vae = vae.vae.half().to(device)
    unet.model = unet.model.half().to(device)
    # Initialize audio processor and Whisper model
    audio_processor = Audio2Feature(model_path="./models/whisper/tiny.pt")
    return vae, unet, pe, timesteps, audio_processor


def load_avatar(avatar_id):
    avatar_path = f"./data/avatars/{avatar_id}"
    full_imgs_path = f"{avatar_path}/full_imgs"
    coords_path = f"{avatar_path}/coords.pkl"
    latents_out_path = f"{avatar_path}/latents.pt"
    mask_out_path = f"{avatar_path}/mask"
    mask_coords_path = f"{avatar_path}/mask_coords.pkl"

    # Check if MuseTalk-specific files exist
    if not os.path.exists(latents_out_path):
        raise FileNotFoundError(f"MuseTalk latents file not found: {latents_out_path}")
    if not os.path.exists(mask_coords_path):
        raise FileNotFoundError(f"MuseTalk mask coords file not found: {mask_coords_path}")
    if not os.path.exists(mask_out_path):
        raise FileNotFoundError(f"MuseTalk mask directory not found: {mask_out_path}")

    input_latent_list_cycle = torch.load(latents_out_path)
    with open(coords_path, 'rb') as f:
        coord_list_cycle = pickle.load(f)
    input_img_list = glob.glob(os.path.join(full_imgs_path, '*.[jpJP][pnPN]*[gG]'))
    input_img_list = sorted(input_img_list, key=lambda x: int(os.path.splitext(os.path.basename(x))[0]))
    frame_list_cycle = read_imgs(input_img_list)
    with open(mask_coords_path, 'rb') as f:
        mask_coords_list_cycle = pickle.load(f)
    input_mask_list = glob.glob(os.path.join(mask_out_path, '*.[jpJP][pnPN]*[gG]'))
    input_mask_list = sorted(input_mask_list, key=lambda x: int(os.path.splitext(os.path.basename(x))[0]))
    mask_list_cycle = read_imgs(input_mask_list)
    return frame_list_cycle, mask_list_cycle, coord_list_cycle, mask_coords_list_cycle, input_latent_list_cycle


@torch.no_grad()
def warm_up(batch_size, model):
    logger.info('warmup model...')
    vae, unet, pe, timesteps, audio_processor = model
    whisper_batch = np.ones((batch_size, 50, 384), dtype=np.uint8)
    latent_batch = torch.ones(batch_size, 8, 32, 32).to(unet.device)

    audio_feature_batch = torch.from_numpy(whisper_batch)
    audio_feature_batch = audio_feature_batch.to(device=unet.device, dtype=unet.model.dtype)
    audio_feature_batch = pe(audio_feature_batch)
    latent_batch = latent_batch.to(dtype=unet.model.dtype)
    pred_latents = unet.model(latent_batch, timesteps, encoder_hidden_states=audio_feature_batch).sample
    vae.decode_latents(pred_latents)


def read_imgs(img_list):
    frames = []
    logger.info('reading images...')
    for img_path in tqdm(img_list):
        frame = cv2.imread(img_path)
        frames.append(frame)
    return frames


def __mirror_index(size, index):
    turn = index // size
    res = index % size
    if turn % 2 == 0:
        return res
    else:
        return size - res - 1


@torch.no_grad()
def inference(render_event, batch_size, input_latent_list_cycle, audio_feat_queue, audio_out_queue, res_frame_queue,
              vae, unet, pe, timesteps):
    length = len(input_latent_list_cycle)
    index = 0
    count = 0
    counttime = 0
    logger.info('start inference')
    while render_event.is_set():
        starttime = time.perf_counter()
        try:
            whisper_chunks = audio_feat_queue.get(block=True, timeout=1)
        except queue.Empty:
            continue
        is_all_silence = True
        audio_frames = []
        for _ in range(batch_size * 2):
            frame, type, eventpoint = audio_out_queue.get()
            audio_frames.append((frame, type, eventpoint))
            if type == 0:
                is_all_silence = False
        if is_all_silence:
            for i in range(batch_size):
                res_frame_queue.put((None, __mirror_index(length, index), audio_frames[i * 2:i * 2 + 2]))
                index = index + 1
        else:
            t = time.perf_counter()
            whisper_batch = np.stack(whisper_chunks)
            latent_batch = []
            for i in range(batch_size):
                idx = __mirror_index(length, index + i)
                latent = input_latent_list_cycle[idx]
                latent_batch.append(latent)
            latent_batch = torch.cat(latent_batch, dim=0)

            audio_feature_batch = torch.from_numpy(whisper_batch)
            audio_feature_batch = audio_feature_batch.to(device=unet.device, dtype=unet.model.dtype)
            audio_feature_batch = pe(audio_feature_batch)
            latent_batch = latent_batch.to(dtype=unet.model.dtype)

            pred_latents = unet.model(latent_batch, timesteps, encoder_hidden_states=audio_feature_batch).sample
            recon = vae.decode_latents(pred_latents)

            counttime += (time.perf_counter() - t)
            count += batch_size
            if count >= 100:
                logger.info(f"------actual avg infer fps:{count/counttime:.4f}")
                count = 0
                counttime = 0
            for i, res_frame in enumerate(recon):
                res_frame_queue.put((res_frame, __mirror_index(length, index), audio_frames[i * 2:i * 2 + 2]))
                index = index + 1
    logger.info('musereal inference processor stop')


class MuseReal(BaseReal):
    @torch.no_grad()
    def __init__(self, opt, model, avatar):
        super().__init__(opt)

        self.fps = opt.fps

        self.batch_size = opt.batch_size
        self.idx = 0
        self.res_frame_queue = mp.Queue(self.batch_size * 2)

        self.vae, self.unet, self.pe, self.timesteps, self.audio_processor = model
        self.frame_list_cycle, self.mask_list_cycle, self.coord_list_cycle, self.mask_coords_list_cycle, self.input_latent_list_cycle = avatar

        self.asr = MuseASR(opt, self, self.audio_processor)
        self.asr.warm_up()
        
        self.render_event = mp.Event()

    def __del__(self):
        logger.info(f'musereal({self.sessionid}) delete')

    def __mirror_index(self, index):
        size = len(self.coord_list_cycle)
        turn = index // size
        res = index % size
        if turn % 2 == 0:
            return res
        else:
            return size - res - 1

    def paste_back_frame(self, pred_frame, idx: int):
        bbox = self.coord_list_cycle[idx]
        ori_frame = copy.deepcopy(self.frame_list_cycle[idx])
        x1, y1, x2, y2 = bbox

        res_frame = cv2.resize(pred_frame.astype(np.uint8), (x2 - x1, y2 - y1))
        mask = self.mask_list_cycle[idx]
        mask_crop_box = self.mask_coords_list_cycle[idx]

        combine_frame = get_image_blending(ori_frame, res_frame, bbox, mask, mask_crop_box)
        return combine_frame

    def render(self, quit_event, loop=None, audio_track=None, video_track=None):
        self.tts.render(quit_event)
        self.init_customindex()
        process_thread = Thread(target=self.process_frames, args=(quit_event, loop, audio_track, video_track))
        process_thread.start()

        self.render_event.set()
        Thread(target=inference, args=(self.render_event, self.batch_size, self.input_latent_list_cycle,
                                       self.asr.feat_queue, self.asr.output_queue, self.res_frame_queue,
                                       self.vae, self.unet, self.pe, self.timesteps)).start()
        while not quit_event.is_set():
            t = time.perf_counter()
            self.asr.run_step()
            if video_track and video_track._queue.qsize() >= 1.5 * self.opt.batch_size:
                logger.debug('sleep qsize=%d', video_track._queue.qsize())
                time.sleep(0.04 * video_track._queue.qsize() * 0.8)
        self.render_event.clear()
        logger.info('musereal thread stop')

__all__ = ["MuseReal", "load_model", "load_avatar", "warm_up"]


