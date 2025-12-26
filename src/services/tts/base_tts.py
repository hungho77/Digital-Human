"""Base TTS service interface."""

from abc import ABC, abstractmethod
import numpy as np


class BaseTTS(ABC):
    """Base class for Text-to-Speech services"""

    @abstractmethod
    async def synthesize(self, text: str) -> np.ndarray:
        """
        Synthesize speech from text.

        Args:
            text: Input text

        Returns:
            audio: Audio samples (float32, 16kHz mono, shape: (samples,))
        """
        pass
