"""Streaming voice activity detection using Silero VAD (torch hub)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Iterator, Optional

import numpy as np


class SileroVadLoadError(RuntimeError):
    """Raised when Silero VAD cannot be loaded."""


@dataclass(frozen=True)
class VadSegment:
    """A detected speech segment."""

    audio: np.ndarray
    start_ms: int
    end_ms: int


class SileroVadSegmenter:
    """Incremental speech segmentation using Silero VAD.

    This segmenter consumes audio frames (float32 mono, 16kHz) and emits
    `VadSegment` objects when a speech segment ends.
    """

    def __init__(
        self,
        *,
        sample_rate_hz: int = 16000,
        min_speech_ms: int = 250,
        min_silence_ms: int = 600,
    ) -> None:
        """Initialize the segmenter.

        Args:
            sample_rate_hz: Input sample rate in Hz (Silero streaming VAD expects 8k or 16k).
            min_speech_ms: Minimum duration (ms) of speech required to emit a segment.
            min_silence_ms: Duration (ms) of silence that closes an active segment.
        """

        if sample_rate_hz not in (8000, 16000):
            raise ValueError("Silero VAD supports 8000Hz or 16000Hz input.")
        self._sample_rate_hz = sample_rate_hz
        self._min_speech_ms = min_speech_ms
        self._min_silence_ms = min_silence_ms

        self._model = None
        self._vad_iterator = None

        self._speech_started_ms: Optional[int] = None
        self._cursor_ms: int = 0
        self._buffer: list[np.ndarray] = []

    def _ensure_loaded(self) -> None:
        """Load Silero VAD model and iterator lazily."""

        if self._model is not None and self._vad_iterator is not None:
            return

        try:
            import torch
        except ImportError as e:  # pragma: no cover
            raise SileroVadLoadError("torch is required for Silero VAD.") from e

        try:
            model, utils = torch.hub.load(
                repo_or_dir="snakers4/silero-vad",
                model="silero_vad",
                trust_repo=True,
                force_reload=False,
            )
            vad_iterator = utils[3]  # VADIterator
        except (OSError, ValueError, RuntimeError) as e:
            raise SileroVadLoadError("Failed to load Silero VAD via torch.hub.") from e

        self._model = model
        self._vad_iterator = vad_iterator(
            model,
            sampling_rate=self._sample_rate_hz,
            min_silence_duration_ms=self._min_silence_ms,
        )

    def reset(self) -> None:
        """Reset internal state (segment buffer and VAD iterator)."""

        self._speech_started_ms = None
        self._cursor_ms = 0
        self._buffer.clear()
        if self._vad_iterator is not None:
            # Silero VADIterator supports state resets.
            self._vad_iterator.reset_states()

    def push_frame(self, frame_f32: np.ndarray) -> Iterator[VadSegment]:
        """Push one audio frame and yield any completed speech segments.

        Args:
            frame_f32: float32 mono frame in [-1, 1] at the configured sample rate.

        Yields:
            VadSegment objects when a speech segment ends.
        """

        self._ensure_loaded()
        assert self._vad_iterator is not None

        frame_len_ms = int(round(1000 * (len(frame_f32) / self._sample_rate_hz)))
        if frame_len_ms <= 0:
            return iter(())

        self._buffer.append(frame_f32)

        import torch

        chunk = torch.from_numpy(frame_f32)
        event = self._vad_iterator(chunk)

        segments: list[VadSegment] = []
        if isinstance(event, dict):
            if "start" in event and self._speech_started_ms is None:
                self._speech_started_ms = int(
                    event["start"] / self._sample_rate_hz * 1000
                )
            if "end" in event and self._speech_started_ms is not None:
                end_ms = int(event["end"] / self._sample_rate_hz * 1000)
                start_ms = self._speech_started_ms

                # Collect full buffered audio and cut to the segment window.
                audio = np.concatenate(self._buffer, axis=0)
                start_sample = int(start_ms * self._sample_rate_hz / 1000)
                end_sample = int(end_ms * self._sample_rate_hz / 1000)
                seg_audio = audio[max(0, start_sample) : max(0, end_sample)]

                if (end_ms - start_ms) >= self._min_speech_ms and seg_audio.size > 0:
                    segments.append(
                        VadSegment(audio=seg_audio, start_ms=start_ms, end_ms=end_ms)
                    )

                # Reset state for next segment.
                self._speech_started_ms = None
                self._buffer.clear()
                self._vad_iterator.reset_states()

        self._cursor_ms += frame_len_ms
        return iter(segments)
