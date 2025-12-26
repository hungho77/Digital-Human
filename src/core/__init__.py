"""Core framework for Pipecat-style pipelines."""

from src.core.frames import (
    Frame,
    TextFrame,
    AudioRawFrame,
    VideoFrame,
    AvatarFrame,
    SystemFrame,
    StartFrame,
    EndFrame,
    CancelFrame,
    ErrorFrame,
)
from src.core.processor import FrameProcessor
from src.core.pipeline import Pipeline
from src.core.context import PipelineContext
from src.core.exceptions import (
    PipelineException,
    ProcessorException,
    TransportException,
    ServiceException,
    AvatarException,
)

__all__ = [
    # Frames
    "Frame",
    "TextFrame",
    "AudioRawFrame",
    "VideoFrame",
    "AvatarFrame",
    "SystemFrame",
    "StartFrame",
    "EndFrame",
    "CancelFrame",
    "ErrorFrame",
    # Core classes
    "FrameProcessor",
    "Pipeline",
    "PipelineContext",
    # Exceptions
    "PipelineException",
    "ProcessorException",
    "TransportException",
    "ServiceException",
    "AvatarException",
]
