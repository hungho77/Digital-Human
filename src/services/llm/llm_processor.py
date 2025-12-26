"""LLM processor wrapper."""

from src.core.processor import FrameProcessor
from src.core.frames import TextFrame
from src.services.llm.base_llm import BaseLLM
from src.utils.logger import logger


class LLMProcessor(FrameProcessor):
    """
    Language Model processor.

    Receives: TextFrame (user input)
    Outputs: TextFrame (LLM response)
    """

    def __init__(self, llm_service: BaseLLM):
        super().__init__(name=f"LLM-{llm_service.__class__.__name__}")
        self.llm = llm_service
        self.conversation_history = []

    async def process_frame(self, frame):
        """Generate LLM response"""
        if isinstance(frame, TextFrame):
            user_text = frame.text
            logger.info(f"User: {user_text}")

            # Add to history
            self.conversation_history.append({"role": "user", "content": user_text})

            try:
                # Generate response
                response = await self.llm.generate(self.conversation_history)

                # Add to history
                self.conversation_history.append(
                    {"role": "assistant", "content": response}
                )

                logger.info(f"Assistant: {response}")

                # Create response frame
                response_frame = TextFrame(
                    text=response,
                    timestamp=frame.timestamp,
                    metadata={
                        "conversation_turn": len(self.conversation_history) // 2
                    },
                )

                await self.push_frame(response_frame)

            except Exception as e:
                logger.error(f"LLM error: {e}")
                await self.push_error(e)
        else:
            # Pass through
            await self.push_frame(frame)
