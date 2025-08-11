###############################################################################
# Ultralight Real Implementation
###############################################################################

import math
import torch
import numpy as np
import os
import time
import cv2
import glob
import pickle
import copy
import queue
from queue import Queue
from threading import Thread, Event
import torch.multiprocessing as mp

from transformers import Wav2Vec2Processor, HubertModel
from src.modules.ultralight.unet import Model
from src.modules.ultralight.audio2feature import Audio2Feature
from src.core.base_real import BaseReal
from src.modules.ultralight.asr import HubertASR
from src.utils.logger import logger
from tqdm import tqdm

device = "cuda" if torch.cuda.is_available() else ("mps" if (hasattr(torch.backends, "mps") and torch.backends.mps.is_available()) else "cpu")

def load_model(opt=None):
    audio_processor = Audio2Feature()
    return audio_processor

def load_avatar(avatar_id):
    avatar_path = f"./data/avatars/{avatar_id}"
    full_imgs_path = f"{avatar_path}/full_imgs"
    face_imgs_path = f"{avatar_path}/face_imgs"
    coords_path = f"{avatar_path}/coords.pkl"
    
    model = Model(6, 'hubert').to(device)
    model.load_state_dict(torch.load(f"{avatar_path}/ultralight.pth"))
    
    with open(coords_path, 'rb') as f:
        coord_list_cycle = pickle.load(f)
    input_img_list = glob.glob(os.path.join(full_imgs_path, '*.[jpJP][pnPN]*[gG]'))
    input_img_list = sorted(input_img_list, key=lambda x: int(os.path.splitext(os.path.basename(x))[0]))
    frame_list_cycle = read_imgs(input_img_list)
    
    input_face_list = glob.glob(os.path.join(face_imgs_path, '*.[jpJP][pnPN]*[gG]'))
    input_face_list = sorted(input_face_list, key=lambda x: int(os.path.splitext(os.path.basename(x))[0]))
    face_list_cycle = read_imgs(input_face_list)

    return model.eval(), frame_list_cycle, face_list_cycle, coord_list_cycle

@torch.no_grad()
def warm_up(batch_size, avatar, modelres):
    logger.info('warmup model...')
    model, _, _, _ = avatar
    img_batch = torch.ones(batch_size, 6, modelres, modelres).to(device)
    mel_batch = torch.ones(batch_size, 32, 32, 32).to(device)
    model(img_batch, mel_batch)

def read_imgs(img_list):
    frames = []
    logger.info('reading images...')
    for img_path in tqdm(img_list):
        frame = cv2.imread(img_path)
        frames.append(frame)
    return frames

def get_audio_features(features, index):
    left = index - 8
    right = index + 8
    pad_left = 0
    pad_right = 0
    if left < 0:
        pad_left = -left
        left = 0
    if right > features.shape[0]:
        pad_right = right - features.shape[0]
        right = features.shape[0]
    auds = torch.from_numpy(features[left:right])
    if pad_left > 0:
        auds = torch.cat([torch.zeros_like(auds[:pad_left]), auds], dim=0)
    if pad_right > 0:
        auds = torch.cat([auds, torch.zeros_like(auds[:pad_right])], dim=0)  # [8, 16]
    return auds

def __mirror_index(size, index):
    turn = index // size
    res = index % size
    if turn % 2 == 0:
        return res
    else:
        return size - res - 1

def inference(quit_event, batch_size, face_list_cycle, audio_feat_queue, audio_out_queue, res_frame_queue, model):
    length = len(face_list_cycle)
    index = 0
    count = 0
    counttime = 0
    logger.info('start inference')

    while not quit_event.is_set():
        try:
            mel_batch = audio_feat_queue.get(block=True, timeout=1)
        except queue.Empty:
            continue
        
        is_all_silence = True
        audio_frames = []
        for _ in range(batch_size * 2):
            frame, type_, eventpoint = audio_out_queue.get()
            audio_frames.append((frame, type_, eventpoint))
            if type_ == 0:
                is_all_silence = False
                
        if is_all_silence:
            for i in range(batch_size):
                res_frame_queue.put((None, __mirror_index(length, index), audio_frames[i * 2:i * 2 + 2]))
                index = index + 1
        else:
            t = time.perf_counter()
            img_batch = []

            for i in range(batch_size):
                idx = __mirror_index(length, index + i)
                crop_img = face_list_cycle[idx]
                img_real_ex = crop_img[4:164, 4:164].copy()
                img_real_ex_ori = img_real_ex.copy()
                img_masked = cv2.rectangle(img_real_ex_ori, (5, 5, 150, 145), (0, 0, 0), -1)

                img_masked = img_masked.transpose(2, 0, 1).astype(np.float32)
                img_real_ex = img_real_ex.transpose(2, 0, 1).astype(np.float32)

                img_real_ex_T = torch.from_numpy(img_real_ex / 255.0)
                img_masked_T = torch.from_numpy(img_masked / 255.0)
                img_concat_T = torch.cat([img_real_ex_T, img_masked_T], axis=0)[None]
                img_batch.append(img_concat_T)

            reshaped_mel_batch = [arr.reshape(32, 32, 32) for arr in mel_batch]
            mel_batch = torch.stack([torch.from_numpy(arr) for arr in reshaped_mel_batch])
            img_batch = torch.stack(img_batch).squeeze(1)

            with torch.no_grad():
                pred = model(img_batch.cuda(), mel_batch.cuda())
            pred = pred.cpu().numpy().transpose(0, 2, 3, 1) * 255.

            counttime += (time.perf_counter() - t)
            count += batch_size
            if count >= 100:
                logger.info(f"------actual avg infer fps:{count / counttime:.4f}")
                count = 0
                counttime = 0
            for i, res_frame in enumerate(pred):
                res_frame_queue.put((res_frame, __mirror_index(length, index), audio_frames[i * 2:i * 2 + 2]))
                index = index + 1

    logger.info('lightreal inference processor stop')


class LightReal(BaseReal):
    @torch.no_grad()
    def __init__(self, opt, model, avatar):
        super().__init__(opt)
        
        self.fps = opt.fps
        self.batch_size = opt.batch_size
        self.idx = 0
        self.res_frame_queue = Queue(self.batch_size * 2)
        
        audio_processor = model
        self.model, self.frame_list_cycle, self.face_list_cycle, self.coord_list_cycle = avatar

        self.asr = HubertASR(opt, self, audio_processor)
        self.asr.warm_up()
        
        self.render_event = mp.Event()
    
    def __del__(self):
        logger.info(f'lightreal({self.sessionid}) delete')

    def paste_back_frame(self, pred_frame, idx: int):
        bbox = self.coord_list_cycle[idx]
        combine_frame = copy.deepcopy(self.frame_list_cycle[idx])
        x1, y1, x2, y2 = bbox

        crop_img = self.face_list_cycle[idx]
        crop_img_ori = crop_img.copy()

        crop_img_ori[4:164, 4:164] = pred_frame.astype(np.uint8)
        crop_img_ori = cv2.resize(crop_img_ori, (x2 - x1, y2 - y1))
        combine_frame[y1:y2, x1:x2] = crop_img_ori
        return combine_frame
            
    def render(self, quit_event, loop=None, audio_track=None, video_track=None):
        self.tts.render(quit_event)
        self.init_customindex()
        process_thread = Thread(target=self.process_frames, args=(quit_event, loop, audio_track, video_track))
        process_thread.start()
        
        Thread(target=inference, args=(quit_event, self.batch_size, self.face_list_cycle, self.asr.feat_queue, self.asr.output_queue, self.res_frame_queue, self.model,)).start()

        while not quit_event.is_set():
            t = time.perf_counter()
            self.asr.run_step()

            if video_track and video_track._queue.qsize() >= 5:
                logger.debug('sleep qsize=%d', video_track._queue.qsize())
                time.sleep(0.04 * video_track._queue.qsize() * 0.8)
                
        logger.info('lightreal thread stop')

__all__ = ["LightReal", "load_model", "load_avatar", "warm_up"]