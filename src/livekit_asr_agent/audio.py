"""Audio conversion helpers for LiveKit audio frames."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class Pcm16Audio:
    """Represents PCM16 interleaved audio.

    Attributes:
        samples: Interleaved int16 samples. For mono, shape is (n,). For stereo,
            shape is (n, 2) after deinterleaving.
        sample_rate_hz: Sample rate in Hz.
        num_channels: Number of channels (1=mono, 2=stereo).
    """

    samples: np.ndarray
    sample_rate_hz: int
    num_channels: int


def pcm16_bytes_to_float32_mono(*, data: memoryview, num_channels: int) -> np.ndarray:
    """Convert PCM16 interleaved bytes to float32 mono in [-1, 1].

    Args:
        data: Audio frame data as a memoryview of int16 samples (interleaved).
        num_channels: Number of channels in the interleaved buffer.

    Returns:
        A float32 numpy array of shape (n_samples,) in [-1, 1].
    """

    pcm = np.frombuffer(data, dtype=np.int16)
    if num_channels <= 1:
        mono_i16 = pcm
    else:
        frames = pcm.reshape(-1, num_channels)
        mono_i16 = frames[:, 0]
    mono_f32 = (mono_i16.astype(np.float32)) / 32768.0
    return mono_f32
