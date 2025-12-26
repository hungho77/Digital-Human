"""WebRTC media stream tracks (moved from services/webrtc.py)."""

import asyncio
import fractions
import time
from typing import Tuple, Union

from aiortc import MediaStreamTrack
from av.frame import Frame
from av.packet import Packet

from src.utils.logger import logger as mylogger

AUDIO_PTIME = 0.020  # 20ms audio packetization
VIDEO_CLOCK_RATE = 90000
VIDEO_PTIME = 0.040  # 1 / 25  # 30fps
VIDEO_TIME_BASE = fractions.Fraction(1, VIDEO_CLOCK_RATE)
SAMPLE_RATE = 16000
AUDIO_TIME_BASE = fractions.Fraction(1, SAMPLE_RATE)


class PlayerStreamTrack(MediaStreamTrack):
    """
    A media stream track for WebRTC playback.

    Handles both audio and video streams with proper timing.
    """

    def __init__(self, player, kind):
        super().__init__()  # don't forget this!
        self.kind = kind
        self._player = player
        self._queue = asyncio.Queue()
        self.timelist = []  # Record timestamps of recent packages
        self.current_frame_count = 0
        if self.kind == "video":
            self.framecount = 0
            self.lasttime = time.perf_counter()
            self.totaltime = 0

    _start: float
    _timestamp: int

    async def next_timestamp(self) -> Tuple[int, fractions.Fraction]:
        """Calculate next timestamp for frame"""
        if self.readyState != "live":
            raise Exception

        if self.kind == "video":
            if hasattr(self, "_timestamp"):
                self._timestamp += int(VIDEO_PTIME * VIDEO_CLOCK_RATE)
                self.current_frame_count += 1
                wait = (
                    self._start + self.current_frame_count * VIDEO_PTIME - time.time()
                )
                if wait > 0:
                    await asyncio.sleep(wait)
            else:
                self._start = time.time()
                self._timestamp = 0
                self.timelist.append(self._start)
                mylogger.info("video start:%f", self._start)
            return self._timestamp, VIDEO_TIME_BASE
        else:  # audio
            if hasattr(self, "_timestamp"):
                self._timestamp += int(AUDIO_PTIME * SAMPLE_RATE)
                self.current_frame_count += 1
                wait = (
                    self._start + self.current_frame_count * AUDIO_PTIME - time.time()
                )
                if wait > 0:
                    await asyncio.sleep(wait)
            else:
                self._start = time.time()
                self._timestamp = 0
                self.timelist.append(self._start)
                mylogger.info("audio start:%f", self._start)
            return self._timestamp, AUDIO_TIME_BASE

    async def recv(self) -> Union[Frame, Packet]:
        """Receive next frame"""
        self._player._start(self)
        frame, eventpoint = await self._queue.get()
        pts, time_base = await self.next_timestamp()
        frame.pts = pts
        frame.time_base = time_base
        if eventpoint:
            self._player.notify(eventpoint)
        if frame is None:
            self.stop()
            raise Exception
        if self.kind == "video":
            self.totaltime += time.perf_counter() - self.lasttime
            self.framecount += 1
            self.lasttime = time.perf_counter()
            if self.framecount == 100:
                mylogger.info(
                    f"------actual avg final fps:{self.framecount / self.totaltime:.4f}"
                )
                self.framecount = 0
                self.totaltime = 0
        return frame

    def stop(self):
        """Stop the track"""
        super().stop()
        if self._player is not None:
            self._player._stop(self)
            self._player = None
