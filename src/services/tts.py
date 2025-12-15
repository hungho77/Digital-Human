from __future__ import annotations

import asyncio
import queue
import time
from enum import Enum
from io import BytesIO
from queue import Queue
from threading import Thread
from typing import TYPE_CHECKING, Iterator

import edge_tts
import numpy as np
import requests
import resampy
import soundfile as sf

if TYPE_CHECKING:
    from src.core.base_real import BaseReal

from src.utils.logger import logger


class State(Enum):
    RUNNING = 0
    PAUSE = 1


class BaseTTS:
    def __init__(self, opt, parent: "BaseReal"):
        self.opt = opt
        self.parent = parent

        self.fps = opt.fps  # 20 ms per frame
        self.sample_rate = 16000
        self.chunk = (
            self.sample_rate // self.fps
        )  # 320 samples per chunk (20ms * 16000 / 1000)
        self.input_stream = BytesIO()

        self.msgqueue = Queue()
        self.state = State.RUNNING

    def flush_talk(self):
        self.msgqueue.queue.clear()
        self.state = State.PAUSE

    def put_msg_txt(self, msg: str, eventpoint=None):
        if len(msg) > 0:
            self.msgqueue.put((msg, eventpoint))

    def render(self, quit_event):
        process_thread = Thread(target=self.process_tts, args=(quit_event,))
        process_thread.start()

    def process_tts(self, quit_event):
        while not quit_event.is_set():
            try:
                msg = self.msgqueue.get(block=True, timeout=1)
                self.state = State.RUNNING
            except queue.Empty:
                continue
            self.txt_to_audio(msg)
        logger.info("ttsreal thread stop")

    def txt_to_audio(self, msg):
        pass


###########################################################################################
class EdgeTTS(BaseTTS):
    def txt_to_audio(self, msg):
        voicename = self.opt.REF_FILE  # "en-US-AriaNeural"
        text, textevent = msg
        t = time.time()
        asyncio.new_event_loop().run_until_complete(self.__main(voicename, text))
        logger.info(f"-------edge tts time:{time.time() - t:.4f}s")
        if self.input_stream.getbuffer().nbytes <= 0:  # edgetts err
            logger.error("edgetts err!!!!!")
            return

        self.input_stream.seek(0)
        stream = self.__create_bytes_stream(self.input_stream)
        streamlen = stream.shape[0]
        idx = 0
        while streamlen >= self.chunk and self.state == State.RUNNING:
            eventpoint = None
            streamlen -= self.chunk
            if idx == 0:
                eventpoint = {"status": "start", "text": text, "msgevent": textevent}
            elif streamlen < self.chunk:
                eventpoint = {"status": "end", "text": text, "msgevent": textevent}
            self.parent.put_audio_frame(stream[idx : idx + self.chunk], eventpoint)
            idx += self.chunk
        self.input_stream.seek(0)
        self.input_stream.truncate()

    def __create_bytes_stream(self, byte_stream):
        stream, sample_rate = sf.read(byte_stream)  # [T*sample_rate,] float64
        logger.info(f"[INFO]tts audio stream {sample_rate}: {stream.shape}")
        stream = stream.astype(np.float32)

        if stream.ndim > 1:
            logger.info(
                f"[WARN] audio has {stream.shape[1]} channels, only use the first."
            )
            stream = stream[:, 0]

        if sample_rate != self.sample_rate and stream.shape[0] > 0:
            logger.info(
                f"[WARN] audio sample rate is {sample_rate}, resampling into {self.sample_rate}."
            )
            stream = resampy.resample(
                x=stream, sr_orig=sample_rate, sr_new=self.sample_rate
            )

        return stream

    async def __main(self, voicename: str, text: str):
        try:
            communicate = edge_tts.Communicate(text, voicename)

            first = True
            async for chunk in communicate.stream():
                if first:
                    first = False
                if chunk["type"] == "audio" and self.state == State.RUNNING:
                    self.input_stream.write(chunk["data"])
                elif chunk["type"] == "WordBoundary":
                    pass
        except Exception as e:
            logger.exception("edgetts: %s", e)


###########################################################################################
class FishTTS(BaseTTS):
    def txt_to_audio(self, msg):
        text, textevent = msg
        self.stream_tts(
            self.fish_speech(
                text,
                self.opt.REF_FILE,
                self.opt.REF_TEXT,
                "en",  # Default to English
                self.opt.TTS_SERVER,  # "http://127.0.0.1:5000"
            ),
            msg,
        )

    def fish_speech(
        self, text, reffile, reftext, language, server_url
    ) -> Iterator[bytes]:
        start = time.perf_counter()
        req = {
            "text": text,
            "reference_id": reffile,
            "format": "wav",
            "streaming": True,
            "use_memory_cache": "on",
        }
        try:
            res = requests.post(
                f"{server_url}/v1/tts",
                json=req,
                stream=True,
                headers={
                    "content-type": "application/json",
                },
            )
            end = time.perf_counter()
            logger.info(f"fish_speech Time to make POST: {end - start}s")

            if res.status_code != 200:
                logger.error("Error:%s", res.text)
                return

            first = True

            for chunk in res.iter_content(chunk_size=17640):  # 1764 44100*20ms*2
                if first:
                    end = time.perf_counter()
                    logger.info(f"fish_speech Time to first chunk: {end - start}s")
                    first = False
                if chunk and self.state == State.RUNNING:
                    yield chunk
        except Exception as e:
            logger.exception("fishtts: %s", e)

    def stream_tts(self, audio_stream, msg):
        text, textevent = msg
        first = True
        for chunk in audio_stream:
            if chunk is not None and len(chunk) > 0:
                stream = np.frombuffer(chunk, dtype=np.int16).astype(np.float32) / 32767
                stream = resampy.resample(
                    x=stream, sr_orig=44100, sr_new=self.sample_rate
                )
                streamlen = stream.shape[0]
                idx = 0
                while streamlen >= self.chunk:
                    eventpoint = None
                    if first:
                        eventpoint = {
                            "status": "start",
                            "text": text,
                            "msgevent": textevent,
                        }
                        first = False
                    self.parent.put_audio_frame(
                        stream[idx : idx + self.chunk], eventpoint
                    )
                    streamlen -= self.chunk
                    idx += self.chunk
        eventpoint = {"status": "end", "text": text, "msgevent": textevent}
        self.parent.put_audio_frame(np.zeros(self.chunk, np.float32), eventpoint)


###########################################################################################
class SovitsTTS(BaseTTS):
    def txt_to_audio(self, msg):
        text, textevent = msg
        self.stream_tts(
            self.gpt_sovits(
                text=text,
                reffile=self.opt.REF_FILE,
                reftext=self.opt.REF_TEXT,
                language="en",  # Default to English
                server_url=self.opt.TTS_SERVER,  # "http://127.0.0.1:5000"
            ),
            msg,
        )

    def gpt_sovits(
        self, text, reffile, reftext, language, server_url
    ) -> Iterator[bytes]:
        start = time.perf_counter()
        req = {
            "text": text,
            "text_lang": language,
            "ref_audio_path": reffile,
            "prompt_text": reftext,
            "prompt_lang": language,
            "media_type": "ogg",
            "streaming_mode": True,
        }
        try:
            res = requests.post(
                f"{server_url}/tts",
                json=req,
                stream=True,
            )
            end = time.perf_counter()
            logger.info(f"gpt_sovits Time to make POST: {end - start}s")

            if res.status_code != 200:
                logger.error("Error:%s", res.text)
                return

            first = True

            for chunk in res.iter_content(chunk_size=None):  # 12800 1280 32K*20ms*2
                logger.info("chunk len:%d", len(chunk))
                if first:
                    end = time.perf_counter()
                    logger.info(f"gpt_sovits Time to first chunk: {end - start}s")
                    first = False
                if chunk and self.state == State.RUNNING:
                    yield chunk
        except Exception as e:
            logger.exception("sovits: %s", e)

    def __create_bytes_stream(self, byte_stream):
        stream, sample_rate = sf.read(byte_stream)  # [T*sample_rate,] float64
        logger.info(f"[INFO]tts audio stream {sample_rate}: {stream.shape}")
        stream = stream.astype(np.float32)

        if stream.ndim > 1:
            logger.info(
                f"[WARN] audio has {stream.shape[1]} channels, only use the first."
            )
            stream = stream[:, 0]

        if sample_rate != self.sample_rate and stream.shape[0] > 0:
            logger.info(
                f"[WARN] audio sample rate is {sample_rate}, resampling into {self.sample_rate}."
            )
            stream = resampy.resample(
                x=stream, sr_orig=sample_rate, sr_new=self.sample_rate
            )

        return stream

    def stream_tts(self, audio_stream, msg):
        text, textevent = msg
        first = True
        for chunk in audio_stream:
            if chunk is not None and len(chunk) > 0:
                byte_stream = BytesIO(chunk)
                stream = self.__create_bytes_stream(byte_stream)
                streamlen = stream.shape[0]
                idx = 0
                while streamlen >= self.chunk:
                    eventpoint = None
                    if first:
                        eventpoint = {
                            "status": "start",
                            "text": text,
                            "msgevent": textevent,
                        }
                        first = False
                    self.parent.put_audio_frame(
                        stream[idx : idx + self.chunk], eventpoint
                    )
                    streamlen -= self.chunk
                    idx += self.chunk
        eventpoint = {"status": "end", "text": text, "msgevent": textevent}
        self.parent.put_audio_frame(np.zeros(self.chunk, np.float32), eventpoint)


###########################################################################################
class CosyVoiceTTS(BaseTTS):
    def txt_to_audio(self, msg):
        text, textevent = msg
        self.stream_tts(
            self.cosy_voice(
                text,
                self.opt.REF_FILE,
                self.opt.REF_TEXT,
                "en",  # Default to English
                self.opt.TTS_SERVER,  # "http://127.0.0.1:5000"
            ),
            msg,
        )

    def cosy_voice(
        self, text, reffile, reftext, language, server_url
    ) -> Iterator[bytes]:
        start = time.perf_counter()
        payload = {"tts_text": text, "prompt_text": reftext}
        try:
            files = [
                (
                    "prompt_wav",
                    ("prompt_wav", open(reffile, "rb"), "application/octet-stream"),
                )
            ]
            res = requests.request(
                "GET",
                f"{server_url}/inference_zero_shot",
                data=payload,
                files=files,
                stream=True,
            )

            end = time.perf_counter()
            logger.info(f"cosy_voice Time to make POST: {end - start}s")

            if res.status_code != 200:
                logger.error("Error:%s", res.text)
                return

            first = True

            for chunk in res.iter_content(chunk_size=9600):  # 960 24K*20ms*2
                if first:
                    end = time.perf_counter()
                    logger.info(f"cosy_voice Time to first chunk: {end - start}s")
                    first = False
                if chunk and self.state == State.RUNNING:
                    yield chunk
        except Exception as e:
            logger.exception("cosyvoice: %s", e)

    def stream_tts(self, audio_stream, msg):
        text, textevent = msg
        first = True
        for chunk in audio_stream:
            if chunk is not None and len(chunk) > 0:
                stream = np.frombuffer(chunk, dtype=np.int16).astype(np.float32) / 32767
                stream = resampy.resample(
                    x=stream, sr_orig=24000, sr_new=self.sample_rate
                )
                streamlen = stream.shape[0]
                idx = 0
                while streamlen >= self.chunk:
                    eventpoint = None
                    if first:
                        eventpoint = {
                            "status": "start",
                            "text": text,
                            "msgevent": textevent,
                        }
                        first = False
                    self.parent.put_audio_frame(
                        stream[idx : idx + self.chunk], eventpoint
                    )
                    streamlen -= self.chunk
                    idx += self.chunk
        eventpoint = {"status": "end", "text": text, "msgevent": textevent}
        self.parent.put_audio_frame(np.zeros(self.chunk, np.float32), eventpoint)


###########################################################################################
class XTTS(BaseTTS):
    def __init__(self, opt, parent):
        super().__init__(opt, parent)
        self.speaker = self.get_speaker(opt.REF_FILE, opt.TTS_SERVER)

    def txt_to_audio(self, msg):
        text, textevent = msg
        self.stream_tts(
            self.xtts(
                text,
                self.speaker,
                "en",  # Default to English
                self.opt.TTS_SERVER,  # "http://localhost:9000"
                "20",  # stream_chunk_size
            ),
            msg,
        )

    def get_speaker(self, ref_audio, server_url):
        files = {"wav_file": ("reference.wav", open(ref_audio, "rb"))}
        response = requests.post(f"{server_url}/clone_speaker", files=files)
        return response.json()

    def xtts(
        self, text, speaker, language, server_url, stream_chunk_size
    ) -> Iterator[bytes]:
        start = time.perf_counter()
        speaker["text"] = text
        speaker["language"] = language
        speaker["stream_chunk_size"] = stream_chunk_size
        try:
            res = requests.post(
                f"{server_url}/tts_stream",
                json=speaker,
                stream=True,
            )
            end = time.perf_counter()
            logger.info(f"xtts Time to make POST: {end - start}s")

            if res.status_code != 200:
                print("Error:", res.text)
                return

            first = True

            for chunk in res.iter_content(chunk_size=9600):  # 24K*20ms*2
                if first:
                    end = time.perf_counter()
                    logger.info(f"xtts Time to first chunk: {end - start}s")
                    first = False
                if chunk:
                    yield chunk
        except Exception as e:
            print(e)

    def stream_tts(self, audio_stream, msg):
        text, textevent = msg
        first = True
        for chunk in audio_stream:
            if chunk is not None and len(chunk) > 0:
                stream = np.frombuffer(chunk, dtype=np.int16).astype(np.float32) / 32767
                stream = resampy.resample(
                    x=stream, sr_orig=24000, sr_new=self.sample_rate
                )
                streamlen = stream.shape[0]
                idx = 0
                while streamlen >= self.chunk:
                    eventpoint = None
                    if first:
                        eventpoint = {
                            "status": "start",
                            "text": text,
                            "msgevent": textevent,
                        }
                        first = False
                    self.parent.put_audio_frame(
                        stream[idx : idx + self.chunk], eventpoint
                    )
                    streamlen -= self.chunk
                    idx += self.chunk
        eventpoint = {"status": "end", "text": text, "msgevent": textevent}
        self.parent.put_audio_frame(np.zeros(self.chunk, np.float32), eventpoint)
