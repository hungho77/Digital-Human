"""Frame data structures for pipeline communication."""

from dataclasses import dataclass, field
from typing import Optional, Any, Dict
import numpy as np
from enum import Enum


class FrameType(Enum):
    """Frame type enumeration"""

    TEXT = "text"
    AUDIO = "audio"
    VIDEO = "video"
    AVATAR = "avatar"
    SYSTEM = "system"


@dataclass
class Frame:
    """Base frame class"""

    timestamp: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def type(self) -> FrameType:
        """Return frame type"""
        return FrameType.SYSTEM


@dataclass
class TextFrame(Frame):
    """Text data frame"""

    text: str
    user_id: Optional[str] = None
    language: str = "en"

    @property
    def type(self) -> FrameType:
        return FrameType.TEXT


@dataclass
class AudioRawFrame(Frame):
    """Raw audio data frame (PCM16)"""

    audio: np.ndarray  # shape: (samples,)
    sample_rate: int = 16000
    num_channels: int = 1

    @property
    def type(self) -> FrameType:
        return FrameType.AUDIO

    def to_bytes(self) -> bytes:
        """Convert to bytes"""
        return (self.audio * 32767).astype(np.int16).tobytes()


@dataclass
class VideoFrame(Frame):
    """Video frame data"""

    image: np.ndarray  # shape: (H, W, 3), BGR format
    width: int
    height: int
    format: str = "bgr24"

    @property
    def type(self) -> FrameType:
        return FrameType.VIDEO


@dataclass
class AvatarFrame(Frame):
    """Generated avatar frame with synced audio"""

    video: np.ndarray  # Talking head frame (H, W, 3)
    audio: Optional[np.ndarray] = None  # Synced audio chunk
    is_speaking: bool = False

    @property
    def type(self) -> FrameType:
        return FrameType.AVATAR


# System frames (control signals)
@dataclass
class SystemFrame(Frame):
    """Base system frame"""

    pass


@dataclass
class StartFrame(SystemFrame):
    """Pipeline start signal"""

    pass


@dataclass
class EndFrame(SystemFrame):
    """Pipeline end signal"""

    pass


@dataclass
class CancelFrame(SystemFrame):
    """Cancel current operation"""

    pass


@dataclass
class ErrorFrame(SystemFrame):
    """Error occurred"""

    error: Exception
    source: Optional[str] = None
