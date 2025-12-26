"""Audio buffering processor."""

import numpy as np
from src.core.processor import FrameProcessor
from src.core.frames import AudioRawFrame
from src.utils.logger import logger


class AudioBufferProcessor(FrameProcessor):
    """
    Audio buffer processor.

    Buffers audio frames until a complete utterance is ready.
    """

    def __init__(self, buffer_size: int = 4800):  # 300ms at 16kHz
        super().__init__(name="AudioBuffer")
        self.buffer_size = buffer_size
        self.buffer = []

    async def process_frame(self, frame):
        """Buffer audio frames"""
        if isinstance(frame, AudioRawFrame):
            self.buffer.append(frame.audio)
            current_size = sum(len(chunk) for chunk in self.buffer)

            if current_size >= self.buffer_size:
                # Concatenate and create new frame
                complete_audio = np.concatenate(self.buffer)
                buffered_frame = AudioRawFrame(
                    audio=complete_audio,
                    sample_rate=frame.sample_rate,
                    timestamp=frame.timestamp,
                )
                await self.push_frame(buffered_frame)

                # Clear buffer
                self.buffer = []
        else:
            # Pass through non-audio frames
            await self.push_frame(frame)
