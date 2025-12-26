"""Base ASR service interface."""

from abc import ABC, abstractmethod
import numpy as np


class BaseASR(ABC):
    """Base class for Automatic Speech Recognition services"""

    @abstractmethod
    async def transcribe(self, audio: np.ndarray) -> str:
        """
        Transcribe audio to text.

        Args:
            audio: Audio samples (float32, 16kHz mono, shape: (samples,))

        Returns:
            text: Transcribed text
        """
        pass
