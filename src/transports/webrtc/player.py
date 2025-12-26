"""WebRTC media player implementation (moved from services/webrtc.py)."""

import asyncio
import threading
from typing import Optional, Set

from aiortc import MediaStreamTrack

from src.transports.webrtc.tracks import PlayerStreamTrack
from src.utils.logger import logger as mylogger


def player_worker_thread(quit_event, loop, container, audio_track, video_track):
    """Worker thread for media player"""
    container.render(quit_event, loop, audio_track, video_track)


class HumanPlayer:
    """
    WebRTC media player for digital human.

    Manages audio and video tracks for streaming avatar output.
    """

    def __init__(
        self, nerfreal, format=None, options=None, timeout=None, loop=False, decode=True
    ):
        self.__thread: Optional[threading.Thread] = None
        self.__thread_quit: Optional[threading.Event] = None

        # examine streams
        self.__started: Set[PlayerStreamTrack] = set()
        self.__audio: Optional[PlayerStreamTrack] = None
        self.__video: Optional[PlayerStreamTrack] = None

        self.__audio = PlayerStreamTrack(self, kind="audio")
        self.__video = PlayerStreamTrack(self, kind="video")

        self.__container = nerfreal

    def notify(self, eventpoint):
        """Notify container of event"""
        self.__container.notify(eventpoint)

    @property
    def audio(self) -> MediaStreamTrack:
        """
        A :class:`aiortc.MediaStreamTrack` instance if the file contains audio.
        """
        return self.__audio

    @property
    def video(self) -> MediaStreamTrack:
        """
        A :class:`aiortc.MediaStreamTrack` instance if the file contains video.
        """
        return self.__video

    def _start(self, track: PlayerStreamTrack) -> None:
        """Start media player thread"""
        self.__started.add(track)
        if self.__thread is None:
            self.__log_debug("Starting worker thread")
            self.__thread_quit = threading.Event()
            self.__thread = threading.Thread(
                name="media-player",
                target=player_worker_thread,
                args=(
                    self.__thread_quit,
                    asyncio.get_event_loop(),
                    self.__container,
                    self.__audio,
                    self.__video,
                ),
            )
            self.__thread.start()

    def _stop(self, track: PlayerStreamTrack) -> None:
        """Stop media player thread"""
        self.__started.discard(track)

        if not self.__started and self.__thread is not None:
            self.__log_debug("Stopping worker thread")
            self.__thread_quit.set()
            self.__thread.join()
            self.__thread = None

        if not self.__started and self.__container is not None:
            self.__container = None

    def __log_debug(self, msg: str, *args) -> None:
        """Log debug message"""
        mylogger.debug(f"HumanPlayer {msg}", *args)
