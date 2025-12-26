"""TTS processor wrapper."""

from src.core.processor import FrameProcessor
from src.core.frames import TextFrame, AudioRawFrame
from src.services.tts.base_tts import BaseTTS
from src.utils.logger import logger


class TTSProcessor(FrameProcessor):
    """
    Text-to-Speech processor.

    Receives: TextFrame
    Outputs: AudioRawFrame
    """

    def __init__(self, tts_service: BaseTTS):
        super().__init__(name=f"TTS-{tts_service.__class__.__name__}")
        self.tts = tts_service

    async def process_frame(self, frame):
        """Convert text to audio"""
        if isinstance(frame, TextFrame):
            try:
                # Call TTS service
                audio = await self.tts.synthesize(frame.text)

                # Create audio frame
                audio_frame = AudioRawFrame(
                    audio=audio,
                    sample_rate=16000,
                    timestamp=frame.timestamp,
                    metadata={"text": frame.text},
                )
                await self.push_frame(audio_frame)

            except Exception as e:
                logger.error(f"TTS error: {e}")
                await self.push_error(e)
        else:
            # Pass through non-text frames
            await self.push_frame(frame)
