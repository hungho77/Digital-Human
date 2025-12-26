# Migration Guide: From Monolithic to Pipecat-Style Architecture

## Overview

This guide provides step-by-step instructions for migrating the Digital Human codebase to the new Pipecat-inspired architecture.

---

## 🎯 Migration Goals

1. **Maintain backward compatibility** during transition
2. **Incremental refactoring** - no big-bang rewrites
3. **Test coverage** for each migration step
4. **Zero downtime** - old and new code coexist temporarily

---

## 📋 Pre-Migration Checklist

- [ ] Backup current codebase
- [ ] Document current API endpoints
- [ ] Create comprehensive test suite for existing functionality
- [ ] Set up feature branch: `refactor/pipecat-architecture`
- [ ] Review and approve architecture proposal

---

## Phase 1: Core Framework Setup (Week 1-2)

### Step 1.1: Create Frame Types

Create `src/core/frames.py`:

```python
"""Frame data structures for pipeline communication."""

from dataclasses import dataclass, field
from typing import Optional, Any, Dict
import numpy as np
from enum import Enum


class FrameType(Enum):
    """Frame type enumeration"""
    TEXT = "text"
    AUDIO = "audio"
    VIDEO = "video"
    AVATAR = "avatar"
    SYSTEM = "system"


@dataclass
class Frame:
    """Base frame class"""
    timestamp: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def type(self) -> FrameType:
        """Return frame type"""
        return FrameType.SYSTEM


@dataclass
class TextFrame(Frame):
    """Text data frame"""
    text: str
    user_id: Optional[str] = None
    language: str = "en"

    @property
    def type(self) -> FrameType:
        return FrameType.TEXT


@dataclass
class AudioRawFrame(Frame):
    """Raw audio data frame (PCM16)"""
    audio: np.ndarray  # shape: (samples,)
    sample_rate: int = 16000
    num_channels: int = 1

    @property
    def type(self) -> FrameType:
        return FrameType.AUDIO

    def to_bytes(self) -> bytes:
        """Convert to bytes"""
        return (self.audio * 32767).astype(np.int16).tobytes()


@dataclass
class VideoFrame(Frame):
    """Video frame data"""
    image: np.ndarray  # shape: (H, W, 3), BGR format
    width: int
    height: int
    format: str = "bgr24"

    @property
    def type(self) -> FrameType:
        return FrameType.VIDEO


@dataclass
class AvatarFrame(Frame):
    """Generated avatar frame with synced audio"""
    video: np.ndarray  # Talking head frame (H, W, 3)
    audio: Optional[np.ndarray] = None  # Synced audio chunk
    is_speaking: bool = False

    @property
    def type(self) -> FrameType:
        return FrameType.AVATAR


# System frames (control signals)
@dataclass
class SystemFrame(Frame):
    """Base system frame"""
    pass


@dataclass
class StartFrame(SystemFrame):
    """Pipeline start signal"""
    pass


@dataclass
class EndFrame(SystemFrame):
    """Pipeline end signal"""
    pass


@dataclass
class CancelFrame(SystemFrame):
    """Cancel current operation"""
    pass


@dataclass
class ErrorFrame(SystemFrame):
    """Error occurred"""
    error: Exception
    source: Optional[str] = None
```

**Test**: `tests/test_frames.py`

```python
import pytest
import numpy as np
from src.core.frames import TextFrame, AudioRawFrame, VideoFrame

def test_text_frame():
    frame = TextFrame(text="Hello", user_id="user123")
    assert frame.text == "Hello"
    assert frame.user_id == "user123"
    assert frame.type.value == "text"

def test_audio_frame():
    audio = np.random.randn(320).astype(np.float32)
    frame = AudioRawFrame(audio=audio, sample_rate=16000)
    assert frame.audio.shape == (320,)
    assert frame.sample_rate == 16000
    assert len(frame.to_bytes()) == 640  # 320 samples * 2 bytes (int16)
```

### Step 1.2: Create Base Processor

Create `src/core/processor.py`:

```python
"""Base frame processor implementation."""

from abc import ABC, abstractmethod
from asyncio import Queue, create_task, CancelledError
from typing import Optional, Callable, List
from src.core.frames import Frame, SystemFrame, ErrorFrame
from src.utils.logger import logger


class FrameProcessor(ABC):
    """Base processor for frame-based pipelines (Pipecat-style)"""

    def __init__(self, name: Optional[str] = None):
        self.name = name or self.__class__.__name__
        self._prev: Optional[FrameProcessor] = None
        self._next: Optional[FrameProcessor] = None

        # Dual-queue system: priority for system frames
        self._input_queue: Queue = Queue()
        self._system_queue: Queue = Queue()

        # Processing control
        self._processing_task = None
        self._running = False

    def link(self, next_processor: 'FrameProcessor') -> 'FrameProcessor':
        """Link this processor to the next one in the chain"""
        self._next = next_processor
        next_processor._prev = self
        logger.debug(f"{self.name} -> {next_processor.name}")
        return next_processor

    async def queue_frame(self, frame: Frame):
        """Queue a frame for processing (called by previous processor)"""
        if isinstance(frame, SystemFrame):
            await self._system_queue.put(frame)
        else:
            await self._input_queue.put(frame)

    async def push_frame(self, frame: Frame):
        """Push frame to next processor (called after processing)"""
        if self._next:
            await self._next.queue_frame(frame)
        else:
            logger.debug(f"{self.name}: No next processor, dropping frame {frame.type}")

    async def push_error(self, error: Exception):
        """Push error upstream"""
        error_frame = ErrorFrame(error=error, source=self.name)
        if self._prev:
            await self._prev.queue_frame(error_frame)
        else:
            logger.error(f"{self.name}: Error with no upstream handler: {error}")

    @abstractmethod
    async def process_frame(self, frame: Frame):
        """
        Process a single frame (override in subclasses)

        Common patterns:
        1. Transform: modify frame and push
        2. Filter: conditionally push or drop
        3. Generate: create new frames and push
        4. Sink: consume frame without pushing
        """
        pass

    async def process(self):
        """Main processing loop"""
        self._running = True
        logger.info(f"{self.name}: Started processing")

        try:
            while self._running:
                # Process system frames first (priority)
                if not self._system_queue.empty():
                    frame = await self._system_queue.get()
                else:
                    frame = await self._input_queue.get()

                try:
                    await self.process_frame(frame)
                except Exception as e:
                    logger.error(f"{self.name}: Error processing frame: {e}")
                    await self.push_error(e)

        except CancelledError:
            logger.info(f"{self.name}: Processing cancelled")
        finally:
            self._running = False
            logger.info(f"{self.name}: Stopped processing")

    async def start(self):
        """Start the processor"""
        if not self._processing_task:
            self._processing_task = create_task(self.process())

    async def stop(self):
        """Stop the processor"""
        self._running = False
        if self._processing_task:
            self._processing_task.cancel()
            try:
                await self._processing_task
            except CancelledError:
                pass
```

**Test**: `tests/test_processor.py`

```python
import pytest
import asyncio
from src.core.processor import FrameProcessor
from src.core.frames import TextFrame, StartFrame

class EchoProcessor(FrameProcessor):
    """Test processor that echoes frames"""
    async def process_frame(self, frame):
        await self.push_frame(frame)

class UppercaseProcessor(FrameProcessor):
    """Test processor that uppercases text"""
    async def process_frame(self, frame):
        if isinstance(frame, TextFrame):
            frame.text = frame.text.upper()
        await self.push_frame(frame)

@pytest.mark.asyncio
async def test_processor_chain():
    results = []

    class CollectorProcessor(FrameProcessor):
        async def process_frame(self, frame):
            results.append(frame)

    # Build chain: Echo -> Uppercase -> Collector
    echo = EchoProcessor()
    upper = UppercaseProcessor()
    collector = CollectorProcessor()

    echo.link(upper).link(collector)

    # Start processors
    await echo.start()
    await upper.start()
    await collector.start()

    # Send frame
    frame = TextFrame(text="hello")
    await echo.queue_frame(frame)

    # Wait for processing
    await asyncio.sleep(0.1)

    # Check result
    assert len(results) == 1
    assert results[0].text == "HELLO"

    # Cleanup
    await echo.stop()
    await upper.stop()
    await collector.stop()
```

### Step 1.3: Create Pipeline Orchestrator

Create `src/core/pipeline.py`:

```python
"""Pipeline orchestration for processor chains."""

from typing import List
import asyncio
from src.core.processor import FrameProcessor
from src.core.frames import StartFrame, EndFrame
from src.utils.logger import logger


class Pipeline:
    """Orchestrates processor chains (Pipecat-style)"""

    def __init__(self, processors: List[FrameProcessor], name: str = "Pipeline"):
        self.name = name
        self.processors = processors
        self._link_processors()
        self._running = False

    def _link_processors(self):
        """Chain processors together"""
        for i in range(len(self.processors) - 1):
            self.processors[i].link(self.processors[i + 1])

    async def start(self):
        """Start all processors and send start frame"""
        logger.info(f"{self.name}: Starting pipeline with {len(self.processors)} processors")

        # Start all processors
        for processor in self.processors:
            await processor.start()

        # Send start frame
        await self.processors[0].queue_frame(StartFrame())

        self._running = True
        logger.info(f"{self.name}: Pipeline started")

    async def stop(self):
        """Stop pipeline"""
        if not self._running:
            return

        logger.info(f"{self.name}: Stopping pipeline")

        # Send end frame
        await self.processors[0].queue_frame(EndFrame())

        # Stop all processors
        for processor in self.processors:
            await processor.stop()

        self._running = False
        logger.info(f"{self.name}: Pipeline stopped")

    async def run(self):
        """Start and wait for pipeline to complete"""
        await self.start()
        # Wait for all processor tasks
        await asyncio.gather(*[p._processing_task for p in self.processors])
```

---

## Phase 2: Refactor Avatar System (Week 3-4)

### Step 2.1: Rename BaseReal → BaseAvatar

**Old**: `src/core/base_real.py`
**New**: `src/processors/avatar/base_avatar.py`

Extract core avatar generation logic:

```python
"""Base avatar processor for generating talking head videos."""

from abc import ABC, abstractmethod
import numpy as np
from src.core.processor import FrameProcessor
from src.core.frames import AudioRawFrame, AvatarFrame
from src.utils.logger import logger


class BaseAvatarProcessor(FrameProcessor, ABC):
    """
    Base class for avatar generation processors.

    Receives: AudioRawFrame
    Outputs: AvatarFrame (video + audio)
    """

    def __init__(self, opt, model, avatar_data):
        super().__init__(name=f"{self.__class__.__name__}")
        self.opt = opt
        self.model = model
        self.avatar_data = avatar_data
        self.sample_rate = 16000
        self.chunk_size = self.sample_rate // opt.fps  # e.g., 320 for 16kHz @ 50fps

    @abstractmethod
    def generate_frame(self, audio_chunk: np.ndarray) -> np.ndarray:
        """
        Generate avatar video frame from audio chunk.

        Args:
            audio_chunk: Audio samples (float32, shape: (chunk_size,))

        Returns:
            video_frame: RGB/BGR image (uint8, shape: (H, W, 3))
        """
        pass

    async def process_frame(self, frame):
        """Process audio frame and generate avatar frame"""
        if isinstance(frame, AudioRawFrame):
            # Generate video frame from audio
            try:
                video = self.generate_frame(frame.audio)
                avatar_frame = AvatarFrame(
                    video=video,
                    audio=frame.audio,
                    is_speaking=self._is_speaking(frame.audio),
                    timestamp=frame.timestamp
                )
                await self.push_frame(avatar_frame)
            except Exception as e:
                logger.error(f"Error generating avatar frame: {e}")
                await self.push_error(e)
        else:
            # Pass through non-audio frames
            await self.push_frame(frame)

    def _is_speaking(self, audio: np.ndarray) -> bool:
        """Determine if audio contains speech (simple energy threshold)"""
        energy = np.abs(audio).mean()
        return energy > 0.01  # Threshold
```

### Step 2.2: Create Specific Avatar Implementations

**Example**: `src/services/avatar_models/musetalk/musetalk_avatar.py`

```python
"""MuseTalk avatar processor implementation."""

import numpy as np
from src.processors.avatar.base_avatar import BaseAvatarProcessor
from src.utils.logger import logger


class MuseTalkAvatarProcessor(BaseAvatarProcessor):
    """MuseTalk-based avatar generation"""

    def generate_frame(self, audio_chunk: np.ndarray) -> np.ndarray:
        """
        Generate avatar frame using MuseTalk model.

        Args:
            audio_chunk: Audio samples (float32, shape: (320,) for 20ms @ 16kHz)

        Returns:
            video_frame: BGR image (uint8, shape: (H, W, 3))
        """
        # TODO: Call MuseTalk model inference
        # This is where the existing MuseTalk logic from modules/musetalk/real.py goes

        # Placeholder
        logger.debug("Generating MuseTalk frame")
        video_frame = np.zeros((512, 512, 3), dtype=np.uint8)
        return video_frame
```

### Step 2.3: Move Model Loading to Service Layer

**Old**: `src/services/real.py` → **New**: `src/services/avatar_models/model_manager.py`

Keep the existing caching logic but return processor instances:

```python
"""Avatar model management and caching."""

from typing import Tuple, Any
from threading import Lock
from src.processors.avatar.base_avatar import BaseAvatarProcessor
from src.utils.logger import logger

_MODEL_CACHE = {}
_CACHE_LOCK = Lock()


def load_avatar_processor(opt) -> BaseAvatarProcessor:
    """
    Load avatar processor for the specified model.

    Args:
        opt: Configuration options (contains opt.model, opt.avatar_id)

    Returns:
        BaseAvatarProcessor instance (MuseTalkAvatarProcessor, Wav2LipAvatarProcessor, etc.)
    """
    model_name = opt.model
    avatar_id = opt.avatar_id
    cache_key = (model_name, avatar_id)

    with _CACHE_LOCK:
        if cache_key in _MODEL_CACHE:
            logger.info(f"Using cached model: {model_name}/{avatar_id}")
            return _MODEL_CACHE[cache_key]

        logger.info(f"Loading model: {model_name}/{avatar_id}")

        # Dynamically import and instantiate
        if model_name == "musetalk":
            from src.services.avatar_models.musetalk import MuseTalkAvatarProcessor
            from src.modules.musetalk.real import load_model, load_avatar, warm_up

            model = load_model()
            avatar_data = load_avatar(avatar_id)
            warm_up(opt.batch_size, model)

            processor = MuseTalkAvatarProcessor(opt, model, avatar_data)

        elif model_name == "wav2lip":
            from src.services.avatar_models.wav2lip import Wav2LipAvatarProcessor
            from src.modules.wav2lip.real import load_model, load_avatar, warm_up

            model = load_model(opt.model_path or "./models/wav2lip/wav2lip.pth")
            avatar_data = load_avatar(avatar_id)
            warm_up(opt.batch_size, model, 256)

            processor = Wav2LipAvatarProcessor(opt, model, avatar_data)

        else:
            raise ValueError(f"Unknown model: {model_name}")

        _MODEL_CACHE[cache_key] = processor
        return processor
```

---

## Phase 3: Service Processors (Week 5-6)

### Step 3.1: Create TTS Processor Wrapper

Create `src/services/tts/tts_processor.py`:

```python
"""TTS processor wrapper."""

from src.core.processor import FrameProcessor
from src.core.frames import TextFrame, AudioRawFrame
from src.services.tts.base_tts import BaseTTS
from src.utils.logger import logger


class TTSProcessor(FrameProcessor):
    """
    Text-to-Speech processor.

    Receives: TextFrame
    Outputs: AudioRawFrame
    """

    def __init__(self, tts_service: BaseTTS):
        super().__init__(name=f"TTS-{tts_service.__class__.__name__}")
        self.tts = tts_service

    async def process_frame(self, frame):
        """Convert text to audio"""
        if isinstance(frame, TextFrame):
            try:
                # Call TTS service
                audio = await self.tts.synthesize(frame.text)

                # Create audio frame
                audio_frame = AudioRawFrame(
                    audio=audio,
                    sample_rate=16000,
                    timestamp=frame.timestamp,
                    metadata={"text": frame.text}
                )
                await self.push_frame(audio_frame)

            except Exception as e:
                logger.error(f"TTS error: {e}")
                await self.push_error(e)
        else:
            # Pass through non-text frames
            await self.push_frame(frame)
```

### Step 3.2: Update Existing TTS Services

Modify `src/services/tts/edgetts.py` to be async:

```python
"""EdgeTTS service implementation."""

import edge_tts
import numpy as np
from src.services.tts.base_tts import BaseTTS
from src.utils.logger import logger


class EdgeTTS(BaseTTS):
    """EdgeTTS text-to-speech service"""

    def __init__(self, voice: str = "en-US-JennyNeural"):
        self.voice = voice

    async def synthesize(self, text: str) -> np.ndarray:
        """
        Synthesize speech from text.

        Args:
            text: Input text

        Returns:
            audio: Audio samples (float32, 16kHz mono, shape: (samples,))
        """
        communicate = edge_tts.Communicate(text, self.voice)

        # Collect audio chunks
        audio_chunks = []
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_chunks.append(chunk["data"])

        # Concatenate and convert to numpy
        audio_bytes = b"".join(audio_chunks)

        # Decode audio (assume 16kHz PCM16)
        audio = np.frombuffer(audio_bytes, dtype=np.int16).astype(np.float32) / 32767.0

        logger.info(f"EdgeTTS synthesized {len(audio)} samples")
        return audio
```

---

## Phase 4: Transport Layer (Week 7-8)

### Step 4.1: Create WebRTC Transport Processor

Create `src/transports/webrtc/webrtc_transport.py`:

```python
"""WebRTC transport processor."""

from src.core.processor import FrameProcessor
from src.core.frames import AudioRawFrame, VideoFrame, AvatarFrame
from src.transports.webrtc.tracks import AudioStreamTrack, VideoStreamTrack
from src.utils.logger import logger


class WebRTCTransport(FrameProcessor):
    """
    WebRTC transport for receiving/sending audio and video.

    Input: User audio/video from WebRTC
    Output: Avatar video/audio to WebRTC
    """

    def __init__(self, audio_track: AudioStreamTrack, video_track: VideoStreamTrack):
        super().__init__(name="WebRTCTransport")
        self.audio_in_track = audio_track
        self.video_out_track = video_track
        self.audio_out_track = AudioStreamTrack()

    async def process_frame(self, frame):
        """Send frames to WebRTC client"""
        if isinstance(frame, AvatarFrame):
            # Send video
            await self.video_out_track.send_frame(frame.video)

            # Send audio
            if frame.audio is not None:
                await self.audio_out_track.send_frame(frame.audio)

        elif isinstance(frame, VideoFrame):
            await self.video_out_track.send_frame(frame.image)

        elif isinstance(frame, AudioRawFrame):
            await self.audio_out_track.send_frame(frame.audio)

        # Always pass through
        await self.push_frame(frame)

    async def receive_audio(self):
        """Receive audio from client and push to pipeline"""
        while self._running:
            audio_data = await self.audio_in_track.receive()
            frame = AudioRawFrame(audio=audio_data, sample_rate=16000)
            await self.push_frame(frame)
```

---

## Phase 5: Integration Example (Week 9-10)

### Complete Pipeline Example

Create `examples/basic_avatar_pipeline.py`:

```python
"""Example: Basic avatar pipeline"""

import asyncio
from src.core.pipeline import Pipeline
from src.processors.avatar.base_avatar import BaseAvatarProcessor
from src.services.tts.tts_processor import TTSProcessor
from src.services.tts.edgetts import EdgeTTS
from src.services.avatar_models.model_manager import load_avatar_processor


class SimpleOptions:
    """Minimal config"""
    model = "musetalk"
    avatar_id = "avatar1"
    fps = 50
    batch_size = 4
    tts = "edgetts"


async def main():
    opt = SimpleOptions()

    # Load processors
    tts_service = EdgeTTS()
    tts_processor = TTSProcessor(tts_service)
    avatar_processor = load_avatar_processor(opt)

    # Build pipeline: Text → Audio → Avatar
    pipeline = Pipeline([
        tts_processor,
        avatar_processor
    ], name="BasicAvatarPipeline")

    # Start
    await pipeline.start()

    # Send text
    from src.core.frames import TextFrame
    text = TextFrame(text="Hello, I am a digital human!")
    await tts_processor.queue_frame(text)

    # Wait
    await asyncio.sleep(5)

    # Stop
    await pipeline.stop()


if __name__ == "__main__":
    asyncio.run(main())
```

---

## 🧪 Testing Strategy

### Unit Tests
- Test each frame type
- Test each processor in isolation
- Mock dependencies

### Integration Tests
- Test processor chains
- Test pipeline orchestration
- Test transport layer

### Performance Tests
- Measure frame throughput
- Measure latency (text → video)
- Memory profiling

---

## 🔄 Backward Compatibility

During migration, maintain old API:

```python
# src/api/routes/webrtc.py

from src.core.pipeline import Pipeline
from src.services.avatar_models.model_manager import load_avatar_processor

# Old endpoint (maintain for now)
@app.post("/api/legacy/start")
async def legacy_start(request):
    # Internally use new pipeline
    opt = parse_options(request)
    avatar = load_avatar_processor(opt)
    # ... build pipeline
    return {"status": "ok"}
```

---

## 📊 Success Metrics

- [ ] All existing tests pass
- [ ] New unit tests cover >80% of new code
- [ ] Performance: <50ms added latency
- [ ] Memory: No significant increase
- [ ] Documentation updated
- [ ] Examples working

---

## 🚧 Rollback Plan

If issues occur:
1. Feature flag: `USE_NEW_ARCHITECTURE=false`
2. Keep old code in `src/legacy/`
3. Gradual rollout: test with 10% traffic first

---

## 📚 Resources

- [Pipecat Documentation](https://github.com/pipecat-ai/pipecat)
- [Architecture Proposal](./ARCHITECTURE_PROPOSAL.md)
- [Python AsyncIO Guide](https://docs.python.org/3/library/asyncio.html)

---

**Questions?** Create an issue or discussion in the repo!
