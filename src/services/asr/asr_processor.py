"""ASR processor wrapper."""

from src.core.processor import FrameProcessor
from src.core.frames import AudioRawFrame, TextFrame
from src.services.asr.base_asr import BaseASR
from src.utils.logger import logger


class ASRProcessor(FrameProcessor):
    """
    Automatic Speech Recognition processor.

    Receives: AudioRawFrame
    Outputs: TextFrame (transcription)
    """

    def __init__(self, asr_service: BaseASR):
        super().__init__(name=f"ASR-{asr_service.__class__.__name__}")
        self.asr = asr_service

    async def process_frame(self, frame):
        """Transcribe audio to text"""
        if isinstance(frame, AudioRawFrame):
            # Only process complete utterances (from VAD)
            if frame.metadata.get("is_complete_utterance"):
                try:
                    # Transcribe
                    text = await self.asr.transcribe(frame.audio)

                    if text.strip():
                        logger.info(f"Transcribed: {text}")

                        # Create text frame
                        text_frame = TextFrame(
                            text=text,
                            timestamp=frame.timestamp,
                            metadata={
                                "audio_duration": len(frame.audio) / frame.sample_rate
                            },
                        )

                        await self.push_frame(text_frame)
                    else:
                        logger.debug("Empty transcription, skipping")

                except Exception as e:
                    logger.error(f"ASR error: {e}")
                    await self.push_error(e)
        else:
            # Pass through
            await self.push_frame(frame)
