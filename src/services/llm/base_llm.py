"""Base LLM service interface."""

from abc import ABC, abstractmethod
from typing import List, Dict


class BaseLLM(ABC):
    """Base class for Language Model services"""

    @abstractmethod
    async def generate(self, messages: List[Dict[str, str]]) -> str:
        """
        Generate response from messages.

        Args:
            messages: List of message dicts with 'role' and 'content'

        Returns:
            response: Generated response text
        """
        pass
