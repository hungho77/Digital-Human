import time
import os
from src.core.base_real import BaseReal

from src.utils.logger import logger


def llm_response(message, nerfreal: "BaseReal"):
    """
    Process LLM response and stream it to the digital human.

    Args:
        message: Input text message
        nerfreal: BaseReal instance to send response to
    """
    start = time.perf_counter()

    try:
        from openai import OpenAI

        client = OpenAI(
            # If you haven't configured environment variables, please replace with your API Key here
            api_key=os.getenv("OPENAI_API_KEY"),
            # Fill in the base_url for OpenAI API
            base_url="https://api.openai.com/v1",
        )
        end = time.perf_counter()
        logger.info(f"llm Time init: {end - start}s")

        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": message},
            ],
            stream=True,
            # Through the following settings, display token usage information in the last line of streaming output
            stream_options={"include_usage": True},
        )

        result = ""
        first = True
        for chunk in completion:
            if len(chunk.choices) > 0:
                if first:
                    end = time.perf_counter()
                    logger.info(f"llm Time to first chunk: {end - start}s")
                    first = False
                msg = chunk.choices[0].delta.content
                if msg is None:
                    continue

                lastpos = 0
                # Split by punctuation marks to create natural speaking segments
                for i, char in enumerate(msg):
                    if char in ",.!;:，。！？：；":
                        result = result + msg[lastpos : i + 1]
                        lastpos = i + 1
                        if len(result) > 10:
                            logger.info(result)
                            nerfreal.put_msg_txt(result)
                            result = ""
                result = result + msg[lastpos:]

        end = time.perf_counter()
        logger.info(f"llm Time to last chunk: {end - start}s")

        # Send any remaining text
        if result:
            nerfreal.put_msg_txt(result)

    except Exception as e:
        logger.error(f"LLM processing error: {e}")
        # Fallback response
        nerfreal.put_msg_txt(
            "I'm sorry, I'm having trouble processing your request right now."
        )
