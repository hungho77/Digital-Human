"""Voice Activity Detection processor."""

import numpy as np
from src.core.processor import FrameProcessor
from src.core.frames import AudioRawFrame
from src.utils.logger import logger


class VADProcessor(FrameProcessor):
    """
    Voice Activity Detection processor.

    Detects when user starts/stops speaking and buffers complete utterances.
    """

    def __init__(self, threshold: float = 0.5, silence_duration: float = 0.8):
        super().__init__(name="VAD")
        self.threshold = threshold
        self.silence_duration = silence_duration
        self.sample_rate = 16000

        # State
        self.is_speaking = False
        self.silence_frames = 0
        self.max_silence_frames = int(silence_duration * 50)  # 50 fps
        self.audio_buffer = []

    async def process_frame(self, frame):
        """Detect voice activity"""
        if not isinstance(frame, AudioRawFrame):
            await self.push_frame(frame)
            return

        # Calculate energy
        energy = np.sqrt(np.mean(frame.audio**2))

        if energy > self.threshold:
            # Speech detected
            if not self.is_speaking:
                logger.info("Speech started")
                self.is_speaking = True
                self.audio_buffer = []

            self.audio_buffer.append(frame.audio)
            self.silence_frames = 0

        else:
            # Silence
            if self.is_speaking:
                self.silence_frames += 1

                if self.silence_frames >= self.max_silence_frames:
                    # Speech ended
                    logger.info(f"Speech ended ({len(self.audio_buffer)} chunks)")

                    # Concatenate all audio
                    complete_audio = np.concatenate(self.audio_buffer)

                    # Create frame with complete utterance
                    utterance_frame = AudioRawFrame(
                        audio=complete_audio,
                        sample_rate=self.sample_rate,
                        metadata={"is_complete_utterance": True},
                    )

                    # Push complete utterance
                    await self.push_frame(utterance_frame)

                    # Reset
                    self.is_speaking = False
                    self.silence_frames = 0
                    self.audio_buffer = []
