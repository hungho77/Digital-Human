# Complete Pipeline Example: Conversational Avatar

This document demonstrates a complete, working example of the new Pipecat-inspired architecture for a conversational digital human.

---

## 🎯 Use Case: Customer Service Avatar

**Scenario**: A customer speaks to a digital human avatar that:
1. Listens to their question (ASR)
2. Understands and generates a response (LLM)
3. Speaks the response (TTS)
4. Shows a realistic talking head (Avatar)
5. Streams back via WebRTC

---

## 📊 Data Flow Diagram

```
┌─────────────┐
│   User      │
│  (WebRTC)   │
└──────┬──────┘
       │ Audio (speaking)
       ▼
┌─────────────────────────────────────────────────────────────┐
│                    WebRTCTransport                          │
│  - Receives audio from user                                 │
│  - Sends avatar video/audio to user                         │
└──────┬──────────────────────────────────────────────────────┘
       │ AudioRawFrame
       ▼
┌─────────────────────────────────────────────────────────────┐
│                    VADProcessor                             │
│  - Detects voice activity                                   │
│  - Buffers audio until speech ends                          │
└──────┬──────────────────────────────────────────────────────┘
       │ AudioRawFrame (complete utterance)
       ▼
┌─────────────────────────────────────────────────────────────┐
│                    ASRProcessor (Whisper)                   │
│  - Transcribes audio to text                                │
└──────┬──────────────────────────────────────────────────────┘
       │ TextFrame("How do I reset my password?")
       ▼
┌─────────────────────────────────────────────────────────────┐
│                    LLMProcessor (GPT-4)                     │
│  - Generates response                                       │
└──────┬──────────────────────────────────────────────────────┘
       │ TextFrame("To reset your password, go to...")
       ▼
┌─────────────────────────────────────────────────────────────┐
│                    TTSProcessor (EdgeTTS)                   │
│  - Synthesizes speech                                       │
└──────┬──────────────────────────────────────────────────────┘
       │ AudioRawFrame (synthesized speech)
       ▼
┌─────────────────────────────────────────────────────────────┐
│              AvatarProcessor (MuseTalk)                     │
│  - Generates talking head video synced to audio             │
└──────┬──────────────────────────────────────────────────────┘
       │ AvatarFrame (video + audio)
       ▼
┌─────────────────────────────────────────────────────────────┐
│                    WebRTCTransport                          │
│  - Streams video/audio to user                              │
└──────┬──────────────────────────────────────────────────────┘
       │ Video/Audio stream
       ▼
┌─────────────┐
│   User      │
│  (sees &    │
│   hears)    │
└─────────────┘
```

---

## 💻 Complete Implementation

### 1. Configuration

```python
# config/avatar_config.py

from pydantic import BaseSettings

class AvatarConfig(BaseSettings):
    """Configuration for conversational avatar"""

    # Avatar model
    avatar_model: str = "musetalk"  # musetalk, wav2lip, ultralight
    avatar_id: str = "avatar1"
    fps: int = 25
    batch_size: int = 4

    # ASR settings
    asr_model: str = "whisper"
    whisper_model_size: str = "base"  # tiny, base, small, medium, large

    # LLM settings
    llm_provider: str = "openai"
    llm_model: str = "gpt-4"
    openai_api_key: str = ""
    system_prompt: str = """You are a helpful customer service representative.
    Keep responses concise (2-3 sentences max)."""

    # TTS settings
    tts_provider: str = "edgetts"
    tts_voice: str = "en-US-JennyNeural"

    # VAD settings
    vad_threshold: float = 0.5
    vad_silence_duration: float = 0.8  # seconds

    # WebRTC
    webrtc_host: str = "0.0.0.0"
    webrtc_port: int = 8080

    class Config:
        env_file = ".env"
```

### 2. Build the Pipeline

```python
# pipelines/conversational_avatar.py

import asyncio
from typing import Optional
from src.core.pipeline import Pipeline
from src.processors.audio.vad_processor import VADProcessor
from src.processors.audio.audio_buffer import AudioBufferProcessor
from src.services.asr.asr_processor import ASRProcessor
from src.services.asr.whisper_asr import WhisperASR
from src.services.llm.llm_processor import LLMProcessor
from src.services.llm.openai_llm import OpenAILLM
from src.services.tts.tts_processor import TTSProcessor
from src.services.tts.edgetts import EdgeTTS
from src.services.avatar_models.model_manager import load_avatar_processor
from src.transports.webrtc.webrtc_transport import WebRTCTransport
from config.avatar_config import AvatarConfig
from src.utils.logger import logger


class ConversationalAvatarPipeline:
    """
    Complete conversational avatar pipeline.

    User Speech → VAD → ASR → LLM → TTS → Avatar → User
    """

    def __init__(self, config: AvatarConfig):
        self.config = config
        self.pipeline: Optional[Pipeline] = None
        self._setup_processors()

    def _setup_processors(self):
        """Initialize all processors"""

        # 1. Transport (bidirectional)
        self.webrtc_transport = WebRTCTransport()

        # 2. VAD (Voice Activity Detection)
        self.vad_processor = VADProcessor(
            threshold=self.config.vad_threshold,
            silence_duration=self.config.vad_silence_duration
        )

        # 3. Audio buffer (collect complete utterances)
        self.audio_buffer = AudioBufferProcessor()

        # 4. ASR (Automatic Speech Recognition)
        asr_service = WhisperASR(model_size=self.config.whisper_model_size)
        self.asr_processor = ASRProcessor(asr_service)

        # 5. LLM (Language Model)
        llm_service = OpenAILLM(
            api_key=self.config.openai_api_key,
            model=self.config.llm_model,
            system_prompt=self.config.system_prompt
        )
        self.llm_processor = LLMProcessor(llm_service)

        # 6. TTS (Text-to-Speech)
        tts_service = EdgeTTS(voice=self.config.tts_voice)
        self.tts_processor = TTSProcessor(tts_service)

        # 7. Avatar (Talking Head Generation)
        # Create minimal options object
        class AvatarOptions:
            model = self.config.avatar_model
            avatar_id = self.config.avatar_id
            fps = self.config.fps
            batch_size = self.config.batch_size

        self.avatar_processor = load_avatar_processor(AvatarOptions())

        # Build pipeline
        self.pipeline = Pipeline([
            self.webrtc_transport,    # Receive audio from user
            self.vad_processor,        # Detect speech
            self.audio_buffer,         # Buffer complete utterance
            self.asr_processor,        # Audio → Text
            self.llm_processor,        # Text → Response
            self.tts_processor,        # Text → Audio
            self.avatar_processor,     # Audio → Video
            self.webrtc_transport      # Send back to user
        ], name="ConversationalAvatar")

    async def start(self):
        """Start the pipeline"""
        logger.info("Starting Conversational Avatar Pipeline")
        await self.pipeline.start()

    async def stop(self):
        """Stop the pipeline"""
        logger.info("Stopping Conversational Avatar Pipeline")
        await self.pipeline.stop()

    async def run(self):
        """Run until interrupted"""
        await self.start()
        try:
            # Keep running
            await asyncio.Event().wait()
        except KeyboardInterrupt:
            logger.info("Interrupted by user")
        finally:
            await self.stop()
```

### 3. Main Application

```python
# app.py

import asyncio
from fastapi import FastAPI, WebSocket
from fastapi.staticfiles import StaticFiles
from aiortc import RTCPeerConnection, RTCSessionDescription
from pipelines.conversational_avatar import ConversationalAvatarPipeline
from config.avatar_config import AvatarConfig
from src.utils.logger import logger

app = FastAPI(title="Digital Human API")

# Serve frontend
app.mount("/static", StaticFiles(directory="static"), name="static")

# Global pipeline instance
config = AvatarConfig()
pipeline: ConversationalAvatarPipeline = None


@app.on_event("startup")
async def startup():
    """Initialize pipeline on startup"""
    global pipeline
    logger.info("Starting Digital Human API")
    pipeline = ConversationalAvatarPipeline(config)
    await pipeline.start()


@app.on_event("shutdown")
async def shutdown():
    """Cleanup on shutdown"""
    global pipeline
    if pipeline:
        await pipeline.stop()
    logger.info("Digital Human API stopped")


@app.post("/api/rtc/offer")
async def webrtc_offer(offer: dict):
    """
    Handle WebRTC offer from client.

    Client sends SDP offer → Server responds with SDP answer
    """
    pc = RTCPeerConnection()

    # Get tracks from pipeline
    audio_track = pipeline.webrtc_transport.audio_out_track
    video_track = pipeline.webrtc_transport.video_out_track

    # Add tracks to connection
    pc.addTrack(audio_track)
    pc.addTrack(video_track)

    # Handle incoming tracks (user audio/video)
    @pc.on("track")
    async def on_track(track):
        logger.info(f"Received track: {track.kind}")
        if track.kind == "audio":
            # Feed audio into pipeline
            pipeline.webrtc_transport.set_input_audio_track(track)

    # Set remote description
    await pc.setRemoteDescription(
        RTCSessionDescription(sdp=offer["sdp"], type=offer["type"])
    )

    # Create answer
    answer = await pc.createAnswer()
    await pc.setLocalDescription(answer)

    return {
        "sdp": pc.localDescription.sdp,
        "type": pc.localDescription.type
    }


@app.get("/api/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "ok",
        "pipeline_running": pipeline is not None and pipeline.pipeline._running
    }


@app.post("/api/message")
async def send_message(message: dict):
    """
    Send text message directly to pipeline (for testing).

    Bypasses ASR, sends text directly to LLM.
    """
    from src.core.frames import TextFrame

    text = message.get("text", "")
    if not text:
        return {"error": "No text provided"}

    # Queue text frame directly to LLM processor
    frame = TextFrame(text=text, user_id=message.get("user_id"))
    await pipeline.llm_processor.queue_frame(frame)

    return {"status": "ok", "message": f"Queued: {text}"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
```

### 4. Processor Implementations

#### VAD Processor

```python
# src/processors/audio/vad_processor.py

import numpy as np
import asyncio
from src.core.processor import FrameProcessor
from src.core.frames import AudioRawFrame
from src.utils.logger import logger


class VADProcessor(FrameProcessor):
    """
    Voice Activity Detection processor.

    Detects when user starts/stops speaking and buffers complete utterances.
    """

    def __init__(self, threshold: float = 0.5, silence_duration: float = 0.8):
        super().__init__(name="VAD")
        self.threshold = threshold
        self.silence_duration = silence_duration
        self.sample_rate = 16000

        # State
        self.is_speaking = False
        self.silence_frames = 0
        self.max_silence_frames = int(silence_duration * 50)  # 50 fps
        self.audio_buffer = []

    async def process_frame(self, frame):
        """Detect voice activity"""
        if not isinstance(frame, AudioRawFrame):
            await self.push_frame(frame)
            return

        # Calculate energy
        energy = np.sqrt(np.mean(frame.audio ** 2))

        if energy > self.threshold:
            # Speech detected
            if not self.is_speaking:
                logger.info("Speech started")
                self.is_speaking = True
                self.audio_buffer = []

            self.audio_buffer.append(frame.audio)
            self.silence_frames = 0

        else:
            # Silence
            if self.is_speaking:
                self.silence_frames += 1

                if self.silence_frames >= self.max_silence_frames:
                    # Speech ended
                    logger.info(f"Speech ended ({len(self.audio_buffer)} chunks)")

                    # Concatenate all audio
                    complete_audio = np.concatenate(self.audio_buffer)

                    # Create frame with complete utterance
                    utterance_frame = AudioRawFrame(
                        audio=complete_audio,
                        sample_rate=self.sample_rate,
                        metadata={"is_complete_utterance": True}
                    )

                    # Push complete utterance
                    await self.push_frame(utterance_frame)

                    # Reset
                    self.is_speaking = False
                    self.silence_frames = 0
                    self.audio_buffer = []
```

#### LLM Processor

```python
# src/services/llm/llm_processor.py

from src.core.processor import FrameProcessor
from src.core.frames import TextFrame
from src.services.llm.base_llm import BaseLLM
from src.utils.logger import logger


class LLMProcessor(FrameProcessor):
    """
    Language Model processor.

    Receives: TextFrame (user input)
    Outputs: TextFrame (LLM response)
    """

    def __init__(self, llm_service: BaseLLM):
        super().__init__(name=f"LLM-{llm_service.__class__.__name__}")
        self.llm = llm_service
        self.conversation_history = []

    async def process_frame(self, frame):
        """Generate LLM response"""
        if isinstance(frame, TextFrame):
            user_text = frame.text
            logger.info(f"User: {user_text}")

            # Add to history
            self.conversation_history.append({"role": "user", "content": user_text})

            try:
                # Generate response
                response = await self.llm.generate(self.conversation_history)

                # Add to history
                self.conversation_history.append({"role": "assistant", "content": response})

                logger.info(f"Assistant: {response}")

                # Create response frame
                response_frame = TextFrame(
                    text=response,
                    timestamp=frame.timestamp,
                    metadata={"conversation_turn": len(self.conversation_history) // 2}
                )

                await self.push_frame(response_frame)

            except Exception as e:
                logger.error(f"LLM error: {e}")
                await self.push_error(e)
        else:
            # Pass through
            await self.push_frame(frame)
```

#### ASR Processor

```python
# src/services/asr/asr_processor.py

from src.core.processor import FrameProcessor
from src.core.frames import AudioRawFrame, TextFrame
from src.services.asr.base_asr import BaseASR
from src.utils.logger import logger


class ASRProcessor(FrameProcessor):
    """
    Automatic Speech Recognition processor.

    Receives: AudioRawFrame
    Outputs: TextFrame (transcription)
    """

    def __init__(self, asr_service: BaseASR):
        super().__init__(name=f"ASR-{asr_service.__class__.__name__}")
        self.asr = asr_service

    async def process_frame(self, frame):
        """Transcribe audio to text"""
        if isinstance(frame, AudioRawFrame):
            # Only process complete utterances (from VAD)
            if frame.metadata.get("is_complete_utterance"):
                try:
                    # Transcribe
                    text = await self.asr.transcribe(frame.audio)

                    if text.strip():
                        logger.info(f"Transcribed: {text}")

                        # Create text frame
                        text_frame = TextFrame(
                            text=text,
                            timestamp=frame.timestamp,
                            metadata={"audio_duration": len(frame.audio) / frame.sample_rate}
                        )

                        await self.push_frame(text_frame)
                    else:
                        logger.debug("Empty transcription, skipping")

                except Exception as e:
                    logger.error(f"ASR error: {e}")
                    await self.push_error(e)
        else:
            # Pass through
            await self.push_frame(frame)
```

---

## 🚀 Running the System

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

```txt
# requirements.txt
fastapi==0.104.1
uvicorn==0.24.0
aiortc==1.6.0
numpy==1.24.3
opencv-python==4.8.1
edge-tts==6.1.9
openai==1.3.5
torch==2.1.0
whisper==1.1.10
pydantic==2.4.2
```

### 2. Configure Environment

```bash
# .env
OPENAI_API_KEY=sk-...
LLM_MODEL=gpt-4
TTS_VOICE=en-US-JennyNeural
AVATAR_MODEL=musetalk
AVATAR_ID=avatar1
```

### 3. Start Server

```bash
python app.py
```

### 4. Open Browser

```
http://localhost:8080
```

---

## 📈 Performance Characteristics

### Expected Latency

| Component | Latency | Notes |
|-----------|---------|-------|
| VAD | ~5ms | Real-time |
| ASR (Whisper base) | ~200ms | Per utterance |
| LLM (GPT-4) | ~1-2s | Depends on response length |
| TTS (EdgeTTS) | ~500ms | Streaming possible |
| Avatar (MuseTalk) | ~40ms/frame | 25fps = 40ms per frame |
| **Total** | **~2-3s** | User speech → Avatar response |

### Optimization Opportunities

1. **Streaming TTS**: Start avatar generation before TTS completes
2. **Streaming LLM**: Stream tokens as they arrive
3. **Batch avatar frames**: Process multiple frames in parallel
4. **Model quantization**: Faster inference with ONNX/TensorRT

---

## 🧪 Testing

```python
# tests/test_pipeline.py

import pytest
import asyncio
import numpy as np
from pipelines.conversational_avatar import ConversationalAvatarPipeline
from config.avatar_config import AvatarConfig
from src.core.frames import TextFrame

@pytest.mark.asyncio
async def test_text_to_avatar():
    """Test complete pipeline: Text → Avatar"""

    config = AvatarConfig(
        llm_provider="mock",  # Use mock LLM for testing
        tts_provider="mock",
        avatar_model="mock"
    )

    pipeline = ConversationalAvatarPipeline(config)
    await pipeline.start()

    # Collect output frames
    output_frames = []

    # Override WebRTC transport to capture outputs
    original_push = pipeline.webrtc_transport.push_frame
    async def capture_push(frame):
        output_frames.append(frame)
        await original_push(frame)

    pipeline.webrtc_transport.push_frame = capture_push

    # Send text
    frame = TextFrame(text="Hello, how are you?")
    await pipeline.llm_processor.queue_frame(frame)

    # Wait for processing
    await asyncio.sleep(2)

    # Verify we got avatar frames
    avatar_frames = [f for f in output_frames if isinstance(f, AvatarFrame)]
    assert len(avatar_frames) > 0, "No avatar frames generated"

    await pipeline.stop()
```

---

## 🎬 Conclusion

This architecture provides:

✅ **Modularity**: Each processor is independent and testable
✅ **Composability**: Build different pipelines for different use cases
✅ **Scalability**: Easy to parallelize and optimize
✅ **Clarity**: Data flow is explicit and traceable
✅ **Flexibility**: Swap components (TTS, LLM, Avatar) without changing pipeline logic

The Pipecat-inspired design transforms the Digital Human codebase from a monolithic system into a composable, maintainable, and extensible framework. 🚀
