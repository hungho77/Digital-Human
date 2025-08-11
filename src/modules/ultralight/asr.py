###############################################################################
# Ultralight HubertASR Implementation
###############################################################################

import time
import torch
import numpy as np
from src.core.asr_base import BaseASR
from src.modules.ultralight.audio2feature import Audio2Feature


class HubertASR(BaseASR):
    """Hubert ASR for ultralight audio feature"""
    
    def __init__(self, opt, parent, audio_processor: Audio2Feature, audio_feat_length=[8, 8]):
        super().__init__(opt, parent)
        self.audio_processor = audio_processor
        self.audio_feat_length = audio_feat_length

    def run_step(self):
        start_time = time.time()
        
        for _ in range(self.batch_size * 2):
            audio_frame, type, eventpoint = self.get_audio_frame()
            self.frames.append(audio_frame)
            self.output_queue.put((audio_frame, type, eventpoint))
        
        if len(self.frames) <= self.stride_left_size + self.stride_right_size:
            return
        
        inputs = np.concatenate(self.frames)  # [N * chunk]

        mel = self.audio_processor.get_hubert_from_16k_speech(inputs)
        mel_chunks = self.audio_processor.feature2chunks(
            feature_array=mel, 
            fps=self.fps/2, 
            batch_size=self.batch_size,
            audio_feat_length=self.audio_feat_length, 
            start=self.stride_left_size/2
        )

        self.feat_queue.put(mel_chunks)
        self.frames = self.frames[-(self.stride_left_size + self.stride_right_size):]

__all__ = ["HubertASR"]