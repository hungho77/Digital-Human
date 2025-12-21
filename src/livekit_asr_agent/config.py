"""Configuration models for the LiveKit ASR agent."""

from __future__ import annotations

import os
from typing import Literal, Optional

from pydantic import BaseModel, Field


class LiveKitAsrAgentConfig(BaseModel):
    """Configuration for the LiveKit ASR agent.

    The agent connects to a LiveKit room, subscribes to microphone audio, runs
    VAD + STT, and publishes transcript messages back to the room.
    """

    # LiveKit connection
    livekit_url: str = Field(
        default="ws://localhost:7880", description="LiveKit WS URL."
    )
    token: str = Field(default="", description="LiveKit access token (JWT).")
    room_name: str = Field(default="asr-room", description="Room to join.")
    identity: str = Field(
        default="asr-agent", description="Participant identity for this agent."
    )

    # Optional filtering: only process a specific remote participant identity
    target_participant_identity: Optional[str] = Field(
        default=None,
        description="If set, only transcribe audio from this participant identity.",
    )

    # Audio processing / resampling
    sample_rate_hz: int = Field(
        default=16000, description="Target sample rate for processing."
    )
    num_channels: int = Field(
        default=1, description="Target number of channels for processing."
    )
    frame_size_ms: int = Field(default=20, description="Audio frame size in ms.")

    # VAD controls (silero)
    min_speech_ms: int = Field(
        default=250, description="Minimum speech duration to emit a segment."
    )
    min_silence_ms: int = Field(
        default=600, description="Silence duration that closes a segment."
    )

    # STT controls (faster-whisper)
    whisper_model: str = Field(
        default="small", description="faster-whisper model name/path."
    )
    device: Literal["cpu", "cuda", "auto"] = Field(
        default="auto", description="Compute device."
    )
    compute_type: str = Field(
        default="auto", description="faster-whisper compute_type."
    )
    language: Optional[str] = Field(
        default=None,
        description="Language code (e.g. 'vi'). If None, auto-detect.",
    )

    # Data message topic
    transcript_topic: str = Field(
        default="asr.transcript", description="LiveKit data topic."
    )

    @classmethod
    def from_env(cls) -> "LiveKitAsrAgentConfig":
        """Load config from environment variables.

        Environment variables (all optional):
        - LIVEKIT_URL
        - LIVEKIT_TOKEN
        - LIVEKIT_ROOM
        - LIVEKIT_IDENTITY
        - LIVEKIT_TARGET_IDENTITY
        - ASR_SAMPLE_RATE_HZ
        - ASR_NUM_CHANNELS
        - ASR_FRAME_SIZE_MS
        - ASR_MIN_SPEECH_MS
        - ASR_MIN_SILENCE_MS
        - ASR_WHISPER_MODEL
        - ASR_DEVICE
        - ASR_COMPUTE_TYPE
        - ASR_LANGUAGE
        - ASR_TRANSCRIPT_TOPIC
        """

        def _get_int(name: str, default: int) -> int:
            raw = os.getenv(name)
            if raw is None or raw.strip() == "":
                return default
            return int(raw)

        return cls(
            livekit_url=os.getenv("LIVEKIT_URL", "ws://localhost:7880"),
            token=os.getenv("LIVEKIT_TOKEN", ""),
            room_name=os.getenv("LIVEKIT_ROOM", "asr-room"),
            identity=os.getenv("LIVEKIT_IDENTITY", "asr-agent"),
            target_participant_identity=os.getenv("LIVEKIT_TARGET_IDENTITY") or None,
            sample_rate_hz=_get_int("ASR_SAMPLE_RATE_HZ", 16000),
            num_channels=_get_int("ASR_NUM_CHANNELS", 1),
            frame_size_ms=_get_int("ASR_FRAME_SIZE_MS", 20),
            min_speech_ms=_get_int("ASR_MIN_SPEECH_MS", 250),
            min_silence_ms=_get_int("ASR_MIN_SILENCE_MS", 600),
            whisper_model=os.getenv("ASR_WHISPER_MODEL", "small"),
            device=os.getenv("ASR_DEVICE", "auto"),  # type: ignore[arg-type]
            compute_type=os.getenv("ASR_COMPUTE_TYPE", "auto"),
            language=os.getenv("ASR_LANGUAGE") or None,
            transcript_topic=os.getenv("ASR_TRANSCRIPT_TOPIC", "asr.transcript"),
        )
