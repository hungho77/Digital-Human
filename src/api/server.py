import os
import sys

# add modules path for vendored code (whisper/musetalk etc.) before other imports
MODULES = os.path.join(
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..")), "modules"
)
if MODULES not in sys.path:
    sys.path.insert(0, MODULES)

import argparse
import asyncio
import gc
import json
import random
from typing import Dict

import aiohttp_cors
from aiohttp import web
from aiortc import (
    RTCConfiguration,
    RTCIceServer,
    RTCPeerConnection,
    RTCSessionDescription,
)
from aiortc.rtcrtpsender import RTCRtpSender

from src.core.base_real import BaseReal
from src.services.llm import llm_response
from src.services.real import build_real, ensure_model_loaded
from src.services.webrtc import HumanPlayer
from src.utils.logger import logger

# Global state
nerfreals: Dict[int, BaseReal] = {}  # sessionid:BaseReal
opt = None
model = None
avatar = None
pcs = set()


def randN(N) -> int:
    """Generate random number of length N"""
    min_val = pow(10, N - 1)
    max_val = pow(10, N)
    return random.randint(min_val, max_val - 1)


def build_nerfreal(sessionid: int) -> BaseReal:
    """Build a BaseReal instance for the given session"""
    opt.sessionid = sessionid
    # Use unified real service
    m, a = ensure_model_loaded(opt)
    return build_real(opt, m, a)


async def offer(request):
    """Handle WebRTC offer"""
    params = await request.json()
    offer = RTCSessionDescription(sdp=params["sdp"], type=params["type"])

    sessionid = randN(6)
    nerfreals[sessionid] = None
    logger.info("sessionid=%d, session num=%d", sessionid, len(nerfreals))
    nerfreal = await asyncio.get_event_loop().run_in_executor(
        None, build_nerfreal, sessionid
    )
    nerfreals[sessionid] = nerfreal

    # Use Google STUN server by default
    ice_server = RTCIceServer(urls="stun:stun.l.google.com:19302")
    pc = RTCPeerConnection(configuration=RTCConfiguration(iceServers=[ice_server]))
    pcs.add(pc)

    @pc.on("connectionstatechange")
    async def on_connectionstatechange():
        logger.info("Connection state is %s" % pc.connectionState)
        if pc.connectionState == "failed":
            await pc.close()
            pcs.discard(pc)
            if sessionid in nerfreals:
                del nerfreals[sessionid]
        if pc.connectionState == "closed":
            pcs.discard(pc)
            if sessionid in nerfreals:
                del nerfreals[sessionid]
            gc.collect()

    player = HumanPlayer(nerfreals[sessionid])
    pc.addTrack(player.audio)
    pc.addTrack(player.video)
    capabilities = RTCRtpSender.getCapabilities("video")
    preferences = list(filter(lambda x: x.name == "H264", capabilities.codecs))
    preferences += list(filter(lambda x: x.name == "VP8", capabilities.codecs))
    preferences += list(filter(lambda x: x.name == "rtx", capabilities.codecs))
    transceiver = pc.getTransceivers()[1]
    transceiver.setCodecPreferences(preferences)

    await pc.setRemoteDescription(offer)

    answer = await pc.createAnswer()
    await pc.setLocalDescription(answer)

    return web.Response(
        content_type="application/json",
        text=json.dumps(
            {
                "sdp": pc.localDescription.sdp,
                "type": pc.localDescription.type,
                "sessionid": sessionid,
            }
        ),
    )


async def human(request):
    """Handle human interaction (chat/echo)"""
    try:
        params = await request.json()

        sessionid = params.get("sessionid", 0)
        if params.get("interrupt"):
            nerfreals[sessionid].flush_talk()

        if params["type"] == "echo":
            nerfreals[sessionid].put_msg_txt(params["text"])
        elif params["type"] == "chat":
            asyncio.get_event_loop().run_in_executor(
                None, llm_response, params["text"], nerfreals[sessionid]
            )

        return web.Response(
            content_type="application/json",
            text=json.dumps({"code": 0, "msg": "ok"}),
        )
    except Exception as e:
        logger.exception("exception:")
        return web.Response(
            content_type="application/json",
            text=json.dumps({"code": -1, "msg": str(e)}),
        )


async def interrupt_talk(request):
    """Handle talk interruption"""
    try:
        params = await request.json()
        sessionid = params.get("sessionid", 0)
        nerfreals[sessionid].flush_talk()

        return web.Response(
            content_type="application/json",
            text=json.dumps({"code": 0, "msg": "ok"}),
        )
    except Exception as e:
        logger.exception("exception:")
        return web.Response(
            content_type="application/json",
            text=json.dumps({"code": -1, "msg": str(e)}),
        )


async def humanaudio(request):
    """Handle audio upload"""
    try:
        form = await request.post()
        sessionid = int(form.get("sessionid", 0))
        fileobj = form["file"]
        # filename = fileobj.filename
        filebytes = fileobj.file.read()
        nerfreals[sessionid].put_audio_file(filebytes)

        return web.Response(
            content_type="application/json",
            text=json.dumps({"code": 0, "msg": "ok"}),
        )
    except Exception as e:
        logger.exception("exception:")
        return web.Response(
            content_type="application/json",
            text=json.dumps({"code": -1, "msg": str(e)}),
        )


async def set_audiotype(request):
    """Set custom audio type"""
    try:
        params = await request.json()
        sessionid = params.get("sessionid", 0)
        nerfreals[sessionid].set_custom_state(params["audiotype"], params["reinit"])

        return web.Response(
            content_type="application/json",
            text=json.dumps({"code": 0, "msg": "ok"}),
        )
    except Exception as e:
        logger.exception("exception:")
        return web.Response(
            content_type="application/json",
            text=json.dumps({"code": -1, "msg": str(e)}),
        )


async def record(request):
    """Handle recording start/stop"""
    try:
        params = await request.json()
        sessionid = params.get("sessionid", 0)

        if params["type"] == "start_record":
            nerfreals[sessionid].start_recording()
        elif params["type"] == "end_record":
            nerfreals[sessionid].stop_recording()

        return web.Response(
            content_type="application/json",
            text=json.dumps({"code": 0, "msg": "ok"}),
        )
    except Exception as e:
        logger.exception("exception:")
        return web.Response(
            content_type="application/json",
            text=json.dumps({"code": -1, "msg": str(e)}),
        )


async def is_speaking(request):
    """Check if avatar is speaking"""
    params = await request.json()
    sessionid = params.get("sessionid", 0)

    return web.Response(
        content_type="application/json",
        text=json.dumps({"code": 0, "data": nerfreals[sessionid].is_speaking()}),
    )


async def on_shutdown(app):
    """Cleanup on server shutdown"""
    coros = [pc.close() for pc in pcs]
    await asyncio.gather(*coros)
    pcs.clear()


def create_app(config):
    """Create and configure the web application"""
    global opt, model, avatar
    opt = config

    # Load model and avatar based on configuration
    # Preload via real service (optional, will cache for sessions)
    ensure_model_loaded(opt)

    # Create aiohttp application
    app = web.Application(client_max_size=1024**2 * 100)
    app.on_shutdown.append(on_shutdown)

    # Add routes
    app.router.add_post("/offer", offer)
    app.router.add_post("/human", human)
    app.router.add_post("/humanaudio", humanaudio)
    app.router.add_post("/set_audiotype", set_audiotype)
    app.router.add_post("/record", record)
    app.router.add_post("/interrupt_talk", interrupt_talk)
    app.router.add_post("/is_speaking", is_speaking)
    app.router.add_static("/", path="web")

    # Configure CORS
    cors = aiohttp_cors.setup(
        app,
        defaults={
            "*": aiohttp_cors.ResourceOptions(
                allow_credentials=True,
                expose_headers="*",
                allow_headers="*",
            )
        },
    )

    # Configure CORS on all routes
    for route in list(app.router.routes()):
        cors.add(route)

    return app


def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description="Digital Human Server")

    # Audio/Video settings
    parser.add_argument("--fps", type=int, default=50, help="Audio fps, must be 50")
    parser.add_argument("-l", type=int, default=10, help="Sliding window left length")
    parser.add_argument("-m", type=int, default=8, help="Sliding window middle length")
    parser.add_argument("-r", type=int, default=10, help="Sliding window right length")
    parser.add_argument("--W", type=int, default=450, help="GUI width")
    parser.add_argument("--H", type=int, default=450, help="GUI height")

    # Model settings
    parser.add_argument(
        "--avatar_id",
        type=str,
        default="avator_1",
        help="Define which avatar in data/avatars",
    )
    parser.add_argument(
        "--batch_size", type=int, default=16, help="Inference batch size"
    )
    parser.add_argument(
        "--customvideo_config", type=str, default="", help="Custom action json config"
    )
    parser.add_argument(
        "--model",
        type=str,
        default="musetalk",
        choices=["musetalk", "wav2lip", "ultralight"],
        help="Model type to use",
    )

    # TTS settings (removed China-specific options)
    parser.add_argument(
        "--tts",
        type=str,
        default="edgetts",
        choices=["edgetts", "gpt-sovits", "xtts", "cosyvoice", "fishtts"],
        help="TTS service type",
    )
    parser.add_argument(
        "--REF_FILE",
        type=str,
        default="en-US-AriaNeural",
        help="Reference voice file or voice ID",
    )
    parser.add_argument(
        "--REF_TEXT", type=str, default=None, help="Reference text for voice cloning"
    )
    parser.add_argument(
        "--TTS_SERVER", type=str, default="http://127.0.0.1:9880", help="TTS server URL"
    )

    # Transport settings
    parser.add_argument(
        "--transport",
        type=str,
        default="webrtc",
        choices=["webrtc", "rtcpush", "virtualcam"],
        help="Transport method",
    )
    parser.add_argument(
        "--push_url",
        type=str,
        default="http://localhost:1985/rtc/v1/whip/?app=live&stream=livestream",
        help="Push URL for RTMP streaming",
    )

    # Server settings
    parser.add_argument(
        "--max_session", type=int, default=1, help="Maximum session count"
    )
    parser.add_argument("--listenport", type=int, default=8010, help="Web listen port")

    return parser.parse_args()


def main():
    """Main entry point"""
    import torch.multiprocessing as mp

    mp.set_start_method("spawn", force=True)

    opt = parse_arguments()

    # Load custom video configuration if specified
    opt.customopt = []
    if opt.customvideo_config:
        with open(opt.customvideo_config, "r") as file:
            opt.customopt = json.load(file)

    # Create and run the application
    app = create_app(opt)

    # Determine the appropriate page based on transport
    pagename = "webrtcapi.html"
    if opt.transport == "rtcpush":
        pagename = "rtcpushapi.html"
    elif opt.transport == "virtualcam":
        pagename = "dashboard.html"

    logger.info(f"Start HTTP server: http://localhost:{opt.listenport}/{pagename}")
    logger.info(
        f"WebRTC integrated frontend: http://localhost:{opt.listenport}/dashboard.html"
    )

    web.run_app(app, host="0.0.0.0", port=opt.listenport)


if __name__ == "__main__":
    main()
