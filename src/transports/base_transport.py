"""Base transport interface."""

from abc import ABC, abstractmethod
from src.core.processor import FrameProcessor


class BaseTransport(FrameProcessor, ABC):
    """
    Base class for transport implementations.

    Transports handle I/O boundaries (WebRTC, VirtualCam, Files, etc.)
    """

    @abstractmethod
    async def send(self, frame):
        """Send frame to output"""
        pass

    @abstractmethod
    async def receive(self):
        """Receive frame from input"""
        pass
