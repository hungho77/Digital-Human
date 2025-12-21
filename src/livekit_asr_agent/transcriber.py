"""Speech-to-text wrapper using faster-whisper."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import numpy as np


class TranscriptionError(RuntimeError):
    """Raised when transcription fails."""


@dataclass(frozen=True)
class TranscriptionResult:
    """A transcription result."""

    text: str


class FasterWhisperTranscriber:
    """Transcriber using `faster-whisper`."""

    def __init__(
        self,
        *,
        model_name_or_path: str,
        device: str = "auto",
        compute_type: str = "auto",
        language: Optional[str] = None,
    ) -> None:
        """Initialize and load the model.

        Args:
            model_name_or_path: Model name (e.g. 'small') or local path.
            device: 'cpu', 'cuda', or 'auto'.
            compute_type: faster-whisper compute_type (e.g. 'int8', 'float16', 'auto').
            language: Optional language code (e.g. 'vi'). If None, auto-detect.
        """

        try:
            from faster_whisper import WhisperModel
        except ImportError as e:  # pragma: no cover
            raise TranscriptionError(
                "faster-whisper is required. Install it with: pip install faster-whisper"
            ) from e

        self._language = language
        self._model = WhisperModel(
            model_name_or_path,
            device=device,
            compute_type=compute_type,
        )

    def transcribe(self, audio_f32: np.ndarray) -> TranscriptionResult:
        """Transcribe a float32 mono audio segment.

        Args:
            audio_f32: float32 mono audio in [-1, 1], typically 16kHz.

        Returns:
            TranscriptionResult with the combined text.
        """

        if audio_f32.size == 0:
            return TranscriptionResult(text="")

        try:
            segments, _info = self._model.transcribe(
                audio_f32,
                language=self._language,
                vad_filter=False,
                beam_size=1,
            )
        except (RuntimeError, ValueError) as e:
            raise TranscriptionError("faster-whisper transcription failed.") from e

        text_parts = []
        for seg in segments:
            if getattr(seg, "text", ""):
                text_parts.append(seg.text.strip())
        return TranscriptionResult(text=" ".join([t for t in text_parts if t]))
