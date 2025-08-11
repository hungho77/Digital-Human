###############################################################################
# Wav2Lip Real Implementation
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

from src.modules.wav2lip.models.wav2lip_v2 import Wav2Lip
from src.core.base_real import BaseReal
from src.modules.wav2lip.asr import LipASR
from src.utils.logger import logger

from tqdm import tqdm

device = "cuda" if torch.cuda.is_available() else ("mps" if (hasattr(torch.backends, "mps") and torch.backends.mps.is_available()) else "cpu")

def _load(checkpoint_path):
    if device == 'cuda':
        checkpoint = torch.load(checkpoint_path)
    else:
        checkpoint = torch.load(checkpoint_path, map_location=lambda storage, loc: storage)
    return checkpoint

def load_model(path="./models/wav2lip/wav2lip.pth"):
    model = Wav2Lip()
    logger.info("Load checkpoint from: {}".format(path))
    checkpoint = _load(path)
    s = checkpoint["state_dict"]
    new_s = {}
    for k, v in s.items():
        new_s[k.replace('module.', '')] = v
    model.load_state_dict(new_s)
    
    model = model.to(device)
    return model.eval()

def load_avatar(avatar_id):
    avatar_path = f"./data/avatars/{avatar_id}"
    full_imgs_path = f"{avatar_path}/full_imgs"
    face_imgs_path = f"{avatar_path}/face_imgs"
    coords_path = f"{avatar_path}/coords.pkl"
    
    with open(coords_path, 'rb') as f:
        coord_list_cycle = pickle.load(f)
    input_img_list = glob.glob(os.path.join(full_imgs_path, '*.[jpJP][pnPN]*[gG]'))
    input_img_list = sorted(input_img_list, key=lambda x: int(os.path.splitext(os.path.basename(x))[0]))
    frame_list_cycle = read_imgs(input_img_list)
    
    input_face_list = glob.glob(os.path.join(face_imgs_path, '*.[jpJP][pnPN]*[gG]'))
    input_face_list = sorted(input_face_list, key=lambda x: int(os.path.splitext(os.path.basename(x))[0]))
    face_list_cycle = read_imgs(input_face_list)

    return frame_list_cycle, face_list_cycle, coord_list_cycle

@torch.no_grad()
def warm_up(batch_size, model, modelres):
    logger.info('warmup model...')
    img_batch = torch.ones(batch_size, 6, modelres, modelres).to(device)
    mel_batch = torch.ones(batch_size, 1, 80, 16).to(device)
    model(mel_batch, img_batch)

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
            # Generate default/idle frames even when no mel features available
            logger.debug("No mel features available, generating idle frames")
            audio_frames = []
            for _ in range(batch_size * 2):
                # Generate silent audio frames for idle state
                frame = np.zeros(1600, dtype=np.float32)  # 0.1s at 16kHz
                audio_frames.append((frame, 1, None))  # type=1 for silence
            
            for i in range(batch_size):
                res_frame_queue.put((None, __mirror_index(length, index), audio_frames[i * 2:i * 2 + 2]))
                index = index + 1
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
            img_batch = []
            for i in range(batch_size):
                idx = __mirror_index(length, index + i)
                face = face_list_cycle[idx]
                img_batch.append(face)
            img_batch, mel_batch = np.asarray(img_batch), np.asarray(mel_batch)

            img_masked = img_batch.copy()
            img_masked[:, face.shape[0]//2:] = 0

            img_batch = np.concatenate((img_masked, img_batch), axis=3) / 255.
            mel_batch = np.reshape(mel_batch, [len(mel_batch), mel_batch.shape[1], mel_batch.shape[2], 1])
            
            img_batch = torch.FloatTensor(np.transpose(img_batch, (0, 3, 1, 2))).to(device)
            mel_batch = torch.FloatTensor(np.transpose(mel_batch, (0, 3, 1, 2))).to(device)

            with torch.no_grad():
                pred = model(mel_batch, img_batch)
            pred = pred.cpu().numpy().transpose(0, 2, 3, 1) * 255.

            counttime += (time.perf_counter() - t)
            count += batch_size
            if count >= 100:
                logger.info(f"------actual avg infer fps:{count/counttime:.4f}")
                count = 0
                counttime = 0
            for i, res_frame in enumerate(pred):
                res_frame_queue.put((res_frame, __mirror_index(length, index), audio_frames[i * 2:i * 2 + 2]))
                index = index + 1
    logger.info('lipreal inference processor stop')


class LipReal(BaseReal):
    @torch.no_grad()
    def __init__(self, opt, model, avatar):
        super().__init__(opt)
        
        self.fps = opt.fps
        self.batch_size = opt.batch_size
        self.idx = 0
        self.res_frame_queue = Queue(self.batch_size * 2)
        
        self.model = model
        self.frame_list_cycle, self.face_list_cycle, self.coord_list_cycle = avatar

        self.asr = LipASR(opt, self)
        self.asr.warm_up()
        
        self.render_event = mp.Event()
    
    def __del__(self):
        logger.info(f'lipreal({self.sessionid}) delete')

    def paste_back_frame(self, pred_frame, idx: int):
        bbox = self.coord_list_cycle[idx]
        combine_frame = copy.deepcopy(self.frame_list_cycle[idx])
        y1, y2, x1, x2 = bbox
        res_frame = cv2.resize(pred_frame.astype(np.uint8), (x2 - x1, y2 - y1))
        combine_frame[y1:y2, x1:x2] = res_frame
        return combine_frame
            
    def render(self, quit_event, loop=None, audio_track=None, video_track=None):
        self.tts.render(quit_event)
        self.init_customindex()
        process_thread = Thread(target=self.process_frames, args=(quit_event, loop, audio_track, video_track))
        process_thread.start()

        Thread(target=inference, args=(quit_event, self.batch_size, self.face_list_cycle,
                                     self.asr.feat_queue, self.asr.output_queue, self.res_frame_queue,
                                     self.model,)).start()

        while not quit_event.is_set():
            t = time.perf_counter()
            self.asr.run_step()

            if video_track and video_track._queue.qsize() >= 5:
                logger.debug('sleep qsize=%d', video_track._queue.qsize())
                time.sleep(0.04 * video_track._queue.qsize() * 0.8)
                
        logger.info('lipreal thread stop')

__all__ = ["LipReal", "load_model", "load_avatar", "warm_up"]