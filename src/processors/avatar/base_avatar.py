"""Base avatar processor for generating talking head videos."""

from abc import ABC, abstractmethod
import numpy as np
from src.core.processor import FrameProcessor
from src.core.frames import AudioRawFrame, AvatarFrame
from src.utils.logger import logger


class BaseAvatarProcessor(FrameProcessor, ABC):
    """
    Base class for avatar generation processors.

    Receives: AudioRawFrame
    Outputs: AvatarFrame (video + audio)
    """

    def __init__(self, opt, model, avatar_data):
        super().__init__(name=f"{self.__class__.__name__}")
        self.opt = opt
        self.model = model
        self.avatar_data = avatar_data
        self.sample_rate = 16000
        self.chunk_size = self.sample_rate // opt.fps  # e.g., 320 for 16kHz @ 50fps

    @abstractmethod
    def generate_frame(self, audio_chunk: np.ndarray) -> np.ndarray:
        """
        Generate avatar video frame from audio chunk.

        Args:
            audio_chunk: Audio samples (float32, shape: (chunk_size,))

        Returns:
            video_frame: RGB/BGR image (uint8, shape: (H, W, 3))
        """
        pass

    async def process_frame(self, frame):
        """Process audio frame and generate avatar frame"""
        if isinstance(frame, AudioRawFrame):
            # Generate video frame from audio
            try:
                video = self.generate_frame(frame.audio)
                avatar_frame = AvatarFrame(
                    video=video,
                    audio=frame.audio,
                    is_speaking=self._is_speaking(frame.audio),
                    timestamp=frame.timestamp,
                )
                await self.push_frame(avatar_frame)
            except Exception as e:
                logger.error(f"Error generating avatar frame: {e}")
                await self.push_error(e)
        else:
            # Pass through non-audio frames
            await self.push_frame(frame)

    def _is_speaking(self, audio: np.ndarray) -> bool:
        """Determine if audio contains speech (simple energy threshold)"""
        energy = np.abs(audio).mean()
        return energy > 0.01  # Threshold
