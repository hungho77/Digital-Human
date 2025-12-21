"""LiveKit ASR agent runtime.

This module connects to a LiveKit room as a participant, subscribes to remote
microphone audio, runs Silero VAD segmentation, transcribes segments with
faster-whisper, and publishes transcript messages back to the room.

Docs referenced:
- LiveKit Python RTC SDK: `livekit.rtc.Room`, `AudioStream`, `AudioFrame`
  (`https://docs.livekit.io/home/client/connect/#installing-the-livekit-sdk`)
"""

from __future__ import annotations

import asyncio
import json
from dataclasses import dataclass
from typing import Optional

from src.livekit_asr_agent.audio import pcm16_bytes_to_float32_mono
from src.livekit_asr_agent.config import LiveKitAsrAgentConfig
from src.livekit_asr_agent.transcriber import FasterWhisperTranscriber
from src.livekit_asr_agent.vad import SileroVadSegmenter


class LiveKitConnectionError(RuntimeError):
    """Raised when the agent cannot connect to LiveKit."""


@dataclass
class _TrackSession:
    """Holds state for one subscribed audio track."""

    participant_identity: str
    track_sid: str
    task: asyncio.Task[None]


class LiveKitAsrAgent:
    """A simple LiveKit participant that performs ASR on remote mic audio."""

    def __init__(self, config: LiveKitAsrAgentConfig) -> None:
        """Create the agent.

        Args:
            config: Runtime configuration.
        """

        self._config = config
        self._track_session: Optional[_TrackSession] = None

        self._segmenter = SileroVadSegmenter(
            sample_rate_hz=config.sample_rate_hz,
            min_speech_ms=config.min_speech_ms,
            min_silence_ms=config.min_silence_ms,
        )
        self._transcriber = FasterWhisperTranscriber(
            model_name_or_path=config.whisper_model,
            device=config.device,
            compute_type=config.compute_type,
            language=config.language,
        )

    async def run(self) -> None:
        """Run the agent until cancelled."""

        if not self._config.token:
            raise LiveKitConnectionError(
                "LIVEKIT_TOKEN is required. Generate one with scripts/mint_livekit_token.py"
            )

        from livekit import rtc

        room = rtc.Room()

        @room.on("track_subscribed")
        def _on_track_subscribed(
            track: rtc.Track, publication, participant
        ) -> None:  # noqa: ANN001
            if not isinstance(track, rtc.RemoteAudioTrack):
                return
            if self._config.target_participant_identity and (
                participant.identity != self._config.target_participant_identity
            ):
                return
            if self._track_session is not None:
                # Only one active mic stream for Day2 minimal pipeline.
                return

            audio_stream = rtc.AudioStream.from_track(
                track=track,
                sample_rate=self._config.sample_rate_hz,
                num_channels=self._config.num_channels,
                frame_size_ms=self._config.frame_size_ms,
            )
            task = asyncio.create_task(
                self._process_audio_stream(
                    room=room,
                    audio_stream=audio_stream,
                    participant_identity=participant.identity,
                    track_sid=track.sid,
                )
            )
            self._track_session = _TrackSession(
                participant_identity=participant.identity,
                track_sid=track.sid,
                task=task,
            )

        try:
            await room.connect(self._config.livekit_url, self._config.token)
        except (rtc.ConnectError, OSError, ValueError) as e:
            raise LiveKitConnectionError("Failed to connect to LiveKit room.") from e

        # Keep running; LiveKit SDK owns callbacks.
        while True:
            await asyncio.sleep(3600)

    async def _process_audio_stream(
        self, *, room, audio_stream, participant_identity: str, track_sid: str
    ) -> None:  # noqa: ANN001
        """Consume audio frames and publish transcripts.

        Args:
            room: LiveKit Room object.
            audio_stream: LiveKit AudioStream iterator.
            participant_identity: Identity of the publisher.
            track_sid: Track SID.
        """

        loop = asyncio.get_running_loop()
        async for event in audio_stream:
            frame = event.frame
            audio_f32 = pcm16_bytes_to_float32_mono(
                data=frame.data,
                num_channels=frame.num_channels,
            )

            for segment in self._segmenter.push_frame(audio_f32):
                # Offload CPU work to executor to avoid blocking the RTC loop.
                result = await loop.run_in_executor(
                    None, self._transcriber.transcribe, segment.audio
                )
                if not result.text:
                    continue

                payload = json.dumps(
                    {
                        "text": result.text,
                        "is_final": True,
                        "start_ms": segment.start_ms,
                        "end_ms": segment.end_ms,
                        "participant": participant_identity,
                        "track_sid": track_sid,
                    }
                )
                await room.local_participant.publish_data(
                    payload,
                    reliable=True,
                    topic=self._config.transcript_topic,
                )


async def run_agent_from_env() -> None:
    """Entrypoint for running the agent using environment configuration."""

    cfg = LiveKitAsrAgentConfig.from_env()
    agent = LiveKitAsrAgent(cfg)
    await agent.run()


def main() -> None:
    """CLI entrypoint."""

    asyncio.run(run_agent_from_env())


if __name__ == "__main__":
    main()
