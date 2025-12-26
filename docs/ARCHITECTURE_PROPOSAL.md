# Digital Human - Pipecat-Inspired Architecture Proposal

## Overview

This proposal reorganizes the Digital Human codebase following Pipecat's frame-based pipeline architecture. The key changes:

1. **Rename "Real" → "Avatar"** - More understandable name for the talking head video generator
2. **Frame-based data flow** - All data (audio, video, text) flows as typed frames
3. **Processor composition** - Small, focused processors instead of monolithic classes
4. **Clean separation** - Transports, Processors, Services, and Pipelines are distinct

---

## 🎯 Core Concepts

### Frame Types
Frames are the atomic units of data flowing through the system:

```python
# src/core/frames.py
from dataclasses import dataclass
from typing import Optional
import numpy as np

@dataclass
class Frame:
    """Base frame class"""
    timestamp: Optional[float] = None

@dataclass
class TextFrame(Frame):
    """Text data (user input, LLM output, transcription)"""
    text: str
    user_id: Optional[str] = None

@dataclass
class AudioRawFrame(Frame):
    """Raw audio data (PCM16, 16kHz mono)"""
    audio: np.ndarray  # shape: (samples,)
    sample_rate: int = 16000
    num_channels: int = 1

@dataclass
class VideoFrame(Frame):
    """Video frame data"""
    image: np.ndarray  # shape: (H, W, 3), BGR format
    width: int
    height: int

@dataclass
class AvatarFrame(Frame):
    """Generated avatar video frame with corresponding audio"""
    video: np.ndarray  # Talking head frame
    audio: np.ndarray  # Synced audio chunk
    is_speaking: bool

@dataclass
class SystemFrame(Frame):
    """Control signals"""
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
```

### Processor Base Class

```python
# src/core/processor.py
from abc import ABC, abstractmethod
from asyncio import Queue
from typing import Optional
from src.core.frames import Frame, SystemFrame

class FrameProcessor(ABC):
    """Base processor following Pipecat pattern"""

    def __init__(self):
        self._prev: Optional[FrameProcessor] = None
        self._next: Optional[FrameProcessor] = None
        self._input_queue: Queue = Queue()
        self._system_queue: Queue = Queue()  # Priority queue for system frames

    def link(self, next_processor: 'FrameProcessor') -> 'FrameProcessor':
        """Link this processor to the next one"""
        self._next = next_processor
        next_processor._prev = self
        return next_processor

    async def queue_frame(self, frame: Frame):
        """Queue a frame for processing"""
        if isinstance(frame, SystemFrame):
            await self._system_queue.put(frame)
        else:
            await self._input_queue.put(frame)

    async def push_frame(self, frame: Frame):
        """Push frame to next processor"""
        if self._next:
            await self._next.queue_frame(frame)

    async def push_error(self, error: Exception):
        """Push error upstream"""
        # Create ErrorFrame and push to previous processor
        pass

    @abstractmethod
    async def process_frame(self, frame: Frame):
        """Process a single frame (override in subclasses)"""
        pass

    async def process(self):
        """Main processing loop"""
        while True:
            # Process system frames first (priority)
            if not self._system_queue.empty():
                frame = await self._system_queue.get()
                await self.process_frame(frame)
            else:
                frame = await self._input_queue.get()
                await self.process_frame(frame)
```

### Pipeline

```python
# src/core/pipeline.py
from typing import List
from src.core.processor import FrameProcessor
from src.core.frames import StartFrame, EndFrame

class Pipeline:
    """Orchestrates processor chains (Pipecat-style)"""

    def __init__(self, processors: List[FrameProcessor]):
        self.processors = processors
        self._link_processors()

    def _link_processors(self):
        """Chain processors together"""
        for i in range(len(self.processors) - 1):
            self.processors[i].link(self.processors[i + 1])

    async def start(self):
        """Start all processors"""
        # Start processing tasks for each processor
        tasks = [asyncio.create_task(p.process()) for p in self.processors]

        # Send start frame
        await self.processors[0].queue_frame(StartFrame())

        await asyncio.gather(*tasks)

    async def stop(self):
        """Stop pipeline"""
        await self.processors[0].queue_frame(EndFrame())
```

---

## 📁 Proposed Directory Structure

```
src/
├── __init__.py
├── app.py                          # Main entry point
│
├── core/                           # Core framework (Pipecat-inspired)
│   ├── __init__.py
│   ├── frames.py                   # Frame data structures ⭐ NEW
│   ├── processor.py                # Base FrameProcessor ⭐ NEW
│   ├── pipeline.py                 # Pipeline orchestration ⭐ NEW
│   ├── context.py                  # Shared context/state ⭐ NEW
│   └── exceptions.py               # Custom exceptions ⭐ NEW
│
├── processors/                     # Frame processors (Pipecat-style)
│   ├── __init__.py
│   │
│   ├── avatar/                     # Avatar generation (renamed from "real") ⭐ RENAMED
│   │   ├── __init__.py
│   │   ├── base_avatar.py          # Base avatar processor interface
│   │   ├── avatar_processor.py     # Main avatar frame processor
│   │   ├── lip_sync_processor.py   # Lip-sync specific processor
│   │   └── frame_composer.py       # Compose video + audio frames
│   │
│   ├── audio/                      # Audio processing
│   │   ├── __init__.py
│   │   ├── audio_buffer.py         # Audio buffering/chunking
│   │   ├── resampler.py            # Audio resampling
│   │   └── vad_processor.py        # Voice activity detection
│   │
│   ├── video/                      # Video processing
│   │   ├── __init__.py
│   │   ├── frame_renderer.py       # Video frame rendering
│   │   └── transition_processor.py # Fade transitions
│   │
│   └── text/                       # Text processing
│       ├── __init__.py
│       └── text_processor.py       # Text preprocessing
│
├── transports/                     # I/O boundaries (Pipecat-style)
│   ├── __init__.py
│   ├── base_transport.py           # Base transport interface
│   │
│   ├── webrtc/                     # WebRTC transport
│   │   ├── __init__.py
│   │   ├── webrtc_transport.py     # WebRTC processor
│   │   ├── player.py               # Media player (from services/webrtc.py)
│   │   └── tracks.py               # Audio/Video track handlers
│   │
│   ├── virtualcam/                 # Virtual camera transport
│   │   ├── __init__.py
│   │   └── virtualcam_transport.py # pyvirtualcam integration
│   │
│   └── local/                      # Local file I/O (testing)
│       ├── __init__.py
│       └── local_transport.py      # File input/output
│
├── services/                       # AI service integrations
│   ├── __init__.py
│   │
│   ├── tts/                        # Text-to-Speech
│   │   ├── __init__.py
│   │   ├── base_tts.py             # Base TTS interface
│   │   ├── tts_processor.py        # TTS frame processor ⭐ NEW
│   │   ├── edgetts.py              # EdgeTTS implementation
│   │   ├── xtts.py                 # XTTS implementation
│   │   ├── cosyvoice.py            # CosyVoice implementation
│   │   ├── gpt_sovits.py           # GPT-SoVITS implementation
│   │   └── fishtts.py              # FishTTS implementation
│   │
│   ├── llm/                        # Large Language Models
│   │   ├── __init__.py
│   │   ├── base_llm.py             # Base LLM interface
│   │   ├── llm_processor.py        # LLM frame processor ⭐ NEW
│   │   ├── openai_llm.py           # OpenAI (GPT-4, etc.)
│   │   ├── anthropic_llm.py        # Anthropic (Claude)
│   │   ├── google_llm.py           # Google (Gemini)
│   │   └── local_llm.py            # vLLM + Qwen3
│   │
│   ├── asr/                        # Automatic Speech Recognition
│   │   ├── __init__.py
│   │   ├── base_asr.py             # Base ASR interface
│   │   ├── asr_processor.py        # ASR frame processor ⭐ NEW
│   │   ├── whisper_asr.py          # Whisper ASR
│   │   └── silero_vad.py           # Silero VAD
│   │
│   └── avatar_models/              # Avatar model implementations (renamed) ⭐ RENAMED
│       ├── __init__.py
│       ├── model_manager.py        # Model loading/caching (from services/real.py)
│       ├── musetalk/               # MuseTalk
│       │   ├── __init__.py
│       │   └── musetalk_avatar.py
│       ├── wav2lip/                # Wav2Lip
│       │   ├── __init__.py
│       │   └── wav2lip_avatar.py
│       ├── ultralight/             # Ultralight
│       │   ├── __init__.py
│       │   └── ultralight_avatar.py
│       └── synctalk/               # SyncTalk (future)
│           ├── __init__.py
│           └── synctalk_avatar.py
│
├── agents/                         # LangGraph conversational agents
│   ├── __init__.py
│   ├── base_agent.py               # Base agent interface
│   ├── orchestrator.py             # Main orchestrator
│   ├── dialogue_agent.py           # Dialogue handling
│   └── reservation_agent.py        # Reservation tasks
│
├── rag/                           # RAG system (Retrieval-Augmented Generation)
│   ├── __init__.py
│   ├── vectorstore.py              # Qdrant/vector DB
│   ├── retriever.py                # Knowledge retrieval
│   ├── embeddings.py               # Embedding generation
│   └── document_loader.py          # Document loading
│
├── api/                           # FastAPI server
│   ├── __init__.py
│   ├── server.py                   # FastAPI app
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── webrtc.py               # WebRTC endpoints
│   │   ├── chat.py                 # Chat endpoints
│   │   └── session.py              # Session management
│   └── middleware/
│       ├── __init__.py
│       ├── cors.py                 # CORS
│       └── error_handler.py        # Error handling
│
├── config/                        # Configuration
│   ├── __init__.py
│   ├── settings.py                 # Pydantic settings
│   └── config_examples.json
│
└── utils/                         # Utilities
    ├── __init__.py
    ├── logger.py
    └── helpers.py
```

---

## 🔄 Example Pipeline Construction

### Scenario: User speaks → Avatar responds

```python
# Example: Building a conversational avatar pipeline

from src.core.pipeline import Pipeline
from src.transports.webrtc import WebRTCTransport
from src.processors.audio import VADProcessor, AudioBuffer
from src.services.asr import WhisperASRProcessor
from src.services.llm import OpenAILLMProcessor
from src.services.tts import EdgeTTSProcessor
from src.processors.avatar import AvatarProcessor
from src.services.avatar_models import MuseTalkAvatar

# Create processors
webrtc = WebRTCTransport()           # Input: WebRTC audio/video
vad = VADProcessor()                  # Detect speech
asr = WhisperASRProcessor()           # Audio → Text
llm = OpenAILLMProcessor()            # Text → Response
tts = EdgeTTSProcessor()              # Text → Audio
avatar = AvatarProcessor(
    model=MuseTalkAvatar()            # Audio → Talking head video
)

# Build pipeline
pipeline = Pipeline([
    webrtc,      # Receive audio from user
    vad,         # Detect voice activity
    asr,         # Transcribe speech
    llm,         # Generate response
    tts,         # Synthesize speech
    avatar,      # Generate talking head
    webrtc       # Send video/audio back
])

# Start
await pipeline.start()
```

### Data Flow:

```
User Speech (WebRTC)
  ↓
AudioRawFrame
  ↓
VADProcessor → AudioRawFrame (with VAD info)
  ↓
WhisperASRProcessor → TextFrame("Hello, how are you?")
  ↓
OpenAILLMProcessor → TextFrame("I'm doing well, thank you!")
  ↓
EdgeTTSProcessor → AudioRawFrame (synthesized speech)
  ↓
AvatarProcessor → AvatarFrame (video + audio)
  ↓
WebRTCTransport → Send to user
```

---

## 🎨 Key Architectural Improvements

### 1. **Small, Focused Processors**
Instead of monolithic `BaseReal`:
- `AvatarProcessor` - Generates talking head frames
- `LipSyncProcessor` - Handles lip synchronization
- `TransitionProcessor` - Smooth transitions between states
- `FrameComposer` - Combines video + audio

### 2. **Service Processors**
Wrap AI services as processors:
- `TTSProcessor(BaseTTS)` - Text → Audio frames
- `LLMProcessor(BaseLLM)` - Text → Text frames
- `ASRProcessor(BaseASR)` - Audio → Text frames

### 3. **Transport Abstraction**
- `WebRTCTransport` - Handles WebRTC I/O
- `VirtualCamTransport` - Outputs to virtual camera
- `LocalTransport` - File-based testing

### 4. **Frame-Based Communication**
Everything flows as typed frames:
- Type safety
- Easy debugging
- Clear data flow
- Composable pipelines

### 5. **Separation of Concerns**

| Layer | Responsibility | Examples |
|-------|----------------|----------|
| **Frames** | Data structures | `AudioFrame`, `VideoFrame`, `TextFrame` |
| **Processors** | Transform frames | `VADProcessor`, `AvatarProcessor` |
| **Services** | AI integrations | `EdgeTTS`, `OpenAI`, `MuseTalk` |
| **Transports** | I/O boundaries | `WebRTC`, `VirtualCam` |
| **Pipeline** | Orchestration | Link processors, manage flow |

---

## 🚀 Migration Strategy

### Phase 1: Core Framework (Week 1-2)
✅ Create frame types (`frames.py`)
✅ Implement `FrameProcessor` base class
✅ Build `Pipeline` orchestrator
✅ Add basic frame flow tests

### Phase 2: Refactor Avatar (Week 3-4)
✅ Rename `BaseReal` → `BaseAvatar`
✅ Extract `AvatarProcessor` from monolithic class
✅ Move video rendering to `FrameRenderer`
✅ Create `LipSyncProcessor`
✅ Update model loading in `services/avatar_models/`

### Phase 3: Service Processors (Week 5-6)
✅ Create `TTSProcessor` wrapper
✅ Create `LLMProcessor` wrapper
✅ Create `ASRProcessor` wrapper
✅ Ensure all services output frames

### Phase 4: Transport Layer (Week 7-8)
✅ Refactor WebRTC as `WebRTCTransport` processor
✅ Create `VirtualCamTransport`
✅ Move `HumanPlayer` to `transports/webrtc/player.py`

### Phase 5: Integration & Testing (Week 9-10)
✅ Build example pipelines
✅ Integration tests
✅ Performance benchmarking
✅ Documentation

---

## 🎯 Benefits

### Developer Experience
- **Easier to understand**: Small, focused components
- **Easier to test**: Each processor can be unit tested
- **Easier to extend**: Add new processors without touching existing code
- **Easier to debug**: Frame flow is explicit and traceable

### Performance
- **Async-first**: Native async/await throughout
- **Parallel processing**: Processors can run concurrently
- **Backpressure**: Queue-based flow control

### Flexibility
- **Swap components**: Change TTS/LLM without pipeline changes
- **Multiple transports**: WebRTC, VirtualCam, or file-based
- **Custom pipelines**: Compose processors for different use cases

---

## 📚 Pipecat Alignment

This architecture directly mirrors Pipecat's design:

| Pipecat Concept | Our Implementation |
|-----------------|-------------------|
| `Frame` | `src/core/frames.py` |
| `FrameProcessor` | `src/core/processor.py` |
| `Pipeline` | `src/core/pipeline.py` |
| `Transport` | `src/transports/` |
| Service integrations | `src/services/` |
| Processor composition | Chain via `.link()` |

---

## ❓ FAQ

**Q: Why rename "Real" to "Avatar"?**
A: "Real" is ambiguous. "Avatar" clearly indicates it's generating a talking head/digital human.

**Q: Is this a complete rewrite?**
A: No. We're refactoring existing code into smaller, composable pieces. Core logic (MuseTalk, Wav2Lip) stays the same.

**Q: Will existing APIs break?**
A: We'll maintain backward compatibility during migration. Old endpoints can internally use the new pipeline.

**Q: What about performance?**
A: Frame-based architecture with async queues typically improves performance through better concurrency.

---

## 🎬 Next Steps

1. **Review & Approve** this proposal
2. **Create feature branch** for refactoring
3. **Implement Phase 1** (core framework)
4. **Test with simple pipeline** (e.g., TTS → Avatar)
5. **Gradually migrate** existing functionality
6. **Update documentation** with new architecture

---

**Questions? Feedback?** Let's discuss! 🚀
