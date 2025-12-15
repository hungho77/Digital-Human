# System Architecture

Comprehensive system architecture documentation for the Digital Human project, detailing component interactions, data flows, and integration points.

## Table of Contents

1. [High-Level Architecture](#high-level-architecture)
2. [Core Components](#core-components)
3. [Data Flow](#data-flow)
4. [Technology Stack](#technology-stack)
5. [Current Implementation](#current-implementation)
6. [Future Enhancements](#future-enhancements)

## High-Level Architecture

### System Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                     Web Interface (Browser)                          │
│              dashboard.html / webrtcapi.html                         │
└────────────────┬────────────────────────────────────────────────────┘
                 │
                 │ WebRTC (Audio/Video Streaming)
                 │
┌────────────────▼────────────────────────────────────────────────────┐
│                   FastAPI Server (app.py)                            │
│                                                                       │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │              WebRTC Handler (aiortc)                          │  │
│  │  - Audio/Video Track Management                               │  │
│  │  - Session Management                                         │  │
│  │  - Real-time Communication                                    │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                                                       │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │              Unified Service Layer                            │  │
│  │                (src/services/)                                │  │
│  │                                                               │  │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐            │  │
│  │  │    TTS     │  │    LLM     │  │   WebRTC   │            │  │
│  │  │  Service   │  │  Service   │  │  Service   │            │  │
│  │  │ (EdgeTTS)  │  │ (OpenAI)   │  │            │            │  │
│  │  └────────────┘  └────────────┘  └────────────┘            │  │
│  │                                                               │  │
│  │  ┌─────────────────────────────────────────────────────┐    │  │
│  │  │          Real Service (src/services/real.py)        │    │  │
│  │  │  - Model Loading & Caching                          │    │  │
│  │  │  - Avatar Generation Coordination                   │    │  │
│  │  └─────────────────────────────────────────────────────┘    │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                                                       │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │               AI Model Modules                                │  │
│  │                 (src/modules/)                                │  │
│  │                                                               │  │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐            │  │
│  │  │  Wav2Lip   │  │ MuseTalk   │  │ Ultralight │            │  │
│  │  │   Module   │  │   Module   │  │   Module   │            │  │
│  │  │            │  │            │  │            │            │  │
│  │  │ - Model    │  │ - Model    │  │ - Model    │            │  │
│  │  │ - Avatar   │  │ - Avatar   │  │ - Avatar   │            │  │
│  │  │ - Inference│  │ - Inference│  │ - Inference│            │  │
│  │  └────────────┘  └────────────┘  └────────────┘            │  │
│  └──────────────────────────────────────────────────────────────┘  │
└───────────────────────────────────────────────────────────────────────┘
                 │
                 │ WebRTC (Animated Avatar + Audio)
                 │
┌────────────────▼────────────────────────────────────────────────────┐
│                     Web Interface (Browser)                          │
└─────────────────────────────────────────────────────────────────────┘
```

### Architecture Principles

**1. Modular Design**
- Each AI model (Wav2Lip, MuseTalk, Ultralight) is a separate module
- Models inherit from BaseReal interface
- Dynamic model loading prevents dependency conflicts

**2. Service Layer Abstraction**
- Clean separation between services (TTS, LLM, WebRTC)
- Unified service manager coordinates all components
- Easy to swap implementations (e.g., different TTS engines)

**3. Real-Time Performance**
- WebRTC for low-latency audio/video streaming
- Efficient model inference with GPU acceleration
- Session management for multiple concurrent users

**4. Configuration Driven**
- Model selection via command-line arguments
- Avatar configuration in YAML files
- Environment-based settings

## Core Components

### 1. FastAPI Server (app.py)

**Purpose:** Main application entry point and HTTP/WebSocket server

**Key Features:**
- REST API endpoints for chat, audio upload, recording
- WebSocket connections for real-time communication
- Session management
- Static file serving for web interface

**Location:** `app.py`

### 2. AI Model Modules (src/modules/)

**Purpose:** Lip-sync and avatar animation using different AI models

#### Wav2Lip Module
```python
# src/modules/wav2lip/real.py

class LipReal(BaseReal):
    """Low-latency audio/video perception pipeline."""

    def __init__(self):
        """Initialize perception components."""
        self.audio_ingest = WebRTCIngest()
        self.vad = SileroVAD()
        self.whisper = WhisperSTT(model="large-v3")
        self.sentiment = SentimentAnalyzer()

    async def process_audio_stream(
        self,
        audio_stream: AsyncIterator[bytes],
        session_id: str
    ) -> AsyncIterator[PerceptionEvent]:
        """Process audio stream into perception events.

        Args:
            audio_stream: Raw audio bytes
            session_id: Session identifier

        Yields:
            PerceptionEvent with transcript, timestamp, sentiment
        """
        async for audio_chunk in audio_stream:
            # Voice Activity Detection
            if not self.vad.is_speech(audio_chunk):
                continue

            # Speech-to-Text
            text, confidence = await self.whisper.transcribe(
                audio_chunk,
                language="vi"
            )

            # Sentiment Analysis
            sentiment = self.sentiment.analyze(text)

            # Create structured event
            event = PerceptionEvent(
                session_id=session_id,
                timestamp=datetime.now(),
                transcript=text,
                confidence=confidence,
                sentiment=sentiment,
                speaker="customer"
            )

            yield event
```

**Key Features:**
- WebRTC for real-time audio/video capture
- VAD (Voice Activity Detection) to filter silence
- Whisper for accurate Vietnamese transcription
- Sentiment analysis for emotional context

**Key Features:**
- Accurate lip-sync with Wav2Lip model
- Face detection and alignment
- Video frame generation with synchronized audio

#### MuseTalk Module
```python
# src/modules/musetalk/real.py

class MuseReal(BaseReal):

```python
# src/agents/orchestrator.py

from langgraph.graph import StateGraph
from typing import Dict, Any

class OrchestratorState(TypedDict):
    """Orchestrator state schema."""
    session_id: str
    active_agent: Optional[str]
    perception_events: List[PerceptionEvent]
    agent_responses: List[AgentResponse]
    health_status: Dict[str, bool]
    error_count: int

class Orchestrator:
    """Central orchestration agent for all sessions."""

    def __init__(self):
        """Initialize orchestrator with all agents."""
        self.dialogue_agent = DialogueAgent()
        self.reservation_agent = ReservationAgent()
        self.sessions: Dict[str, OrchestratorState] = {}

        # Build orchestrator graph
        self.graph = self._build_graph()

    def _build_graph(self) -> StateGraph:
        """Build orchestrator state machine."""
        workflow = StateGraph(OrchestratorState)

        # Nodes
        workflow.add_node("route_event", self._route_perception_event)
        workflow.add_node("handle_dialogue", self._handle_dialogue)
        workflow.add_node("handle_reservation", self._handle_reservation)
        workflow.add_node("error_recovery", self._recover_from_error)
        workflow.add_node("timeout_handler", self._handle_timeout)

        # Conditional routing
        workflow.add_conditional_edges(
            "route_event",
            self._select_agent,
            {
                "dialogue": "handle_dialogue",
                "reservation": "handle_reservation",
                "error": "error_recovery"
            }
        )

        return workflow.compile()

    async def process_perception_event(
        self,
        event: PerceptionEvent
    ) -> AgentResponse:
        """Process perception event through appropriate agent.

        Args:
            event: Perception event from audio pipeline

        Returns:
            Agent response with text and actions
        """
        session_id = event.session_id

        # Get or create session state
        if session_id not in self.sessions:
            self.sessions[session_id] = self._create_session_state(session_id)

        state = self.sessions[session_id]
        state["perception_events"].append(event)

        # Run through orchestrator graph
        result = await self.graph.ainvoke(state)

        return result["agent_responses"][-1]

    def _select_agent(self, state: OrchestratorState) -> str:
        """Select appropriate agent based on state.

        Args:
            state: Current orchestrator state

        Returns:
            Agent name to route to
        """
        latest_event = state["perception_events"][-1]
        intent = classify_intent(latest_event.transcript)

        if intent == "reservation":
            return "reservation"
        elif state["error_count"] > 3:
            return "error"
        else:
            return "dialogue"
```

**Key Features:**
- High-quality facial animation
- Diffusion-based generation
- Advanced expression control

#### Ultralight Module
```python
# src/modules/ultralight/real.py

class LightReal(BaseReal):

```python
# src/agents/dialogue.py

from langgraph.graph import StateGraph
from langchain_core.messages import HumanMessage, AIMessage

class DialogueState(TypedDict):
    """Dialogue agent state."""
    messages: List[Union[HumanMessage, AIMessage]]
    customer_name: Optional[str]
    intent: Optional[str]
    context: Dict[str, Any]
    reservation_details: Optional[Dict]
    conversation_history: List[Dict]

class DialogueAgent:
    """Main conversation agent with RAG capabilities."""

    def __init__(self, knowledge_base: RestaurantKnowledgeBase):
        """Initialize dialogue agent.

        Args:
            knowledge_base: RAG system for restaurant info
        """
        self.kb = knowledge_base
        self.llm = ChatOpenAI(temperature=0.7)
        self.graph = self._build_graph()

    def _build_graph(self) -> StateGraph:
        """Build dialogue agent workflow."""
        workflow = StateGraph(DialogueState)

        # Nodes
        workflow.add_node("understand_intent", self._classify_intent)
        workflow.add_node("extract_entities", self._extract_entities)
        workflow.add_node("rag_query", self._query_knowledge_base)
        workflow.add_node("generate_response", self._generate_response)
        workflow.add_node("handoff_reservation", self._handoff_to_reservation)

        # Flow
        workflow.set_entry_point("understand_intent")
        workflow.add_edge("understand_intent", "extract_entities")

        # Conditional routing based on intent
        workflow.add_conditional_edges(
            "extract_entities",
            self._route_by_intent,
            {
                "reservation": "handoff_reservation",
                "faq": "rag_query",
                "general": "generate_response"
            }
        )

        workflow.add_edge("rag_query", "generate_response")

        return workflow.compile()

    async def process(
        self,
        customer_message: str,
        context: Dict[str, Any]
    ) -> Tuple[str, Dict[str, Any]]:
        """Process customer message and generate response.

        Args:
            customer_message: Customer's input text
            context: Conversation context

        Returns:
            Tuple of (response_text, updated_context)
        """
        # Create initial state
        state = DialogueState(
            messages=[HumanMessage(content=customer_message)],
            context=context,
            customer_name=context.get("customer_name"),
            intent=None,
            reservation_details=None,
            conversation_history=context.get("history", [])
        )

        # Run through dialogue graph
        result = await self.graph.ainvoke(state)

        # Extract response
        response = result["messages"][-1].content
        updated_context = result["context"]

        return response, updated_context

    def _classify_intent(self, state: DialogueState) -> DialogueState:
        """Classify customer intent using LLM.

        Args:
            state: Current dialogue state

        Returns:
            Updated state with intent classification
        """
        message = state["messages"][-1].content

        # Use LLM for intent classification
        prompt = f"""Classify the intent of this Vietnamese customer message:
        Message: {message}

        Intents: reservation, menu_inquiry, faq, complaint, general

        Intent:"""

        response = self.llm.invoke(prompt)
        intent = response.content.strip().lower()

        return {
            **state,
            "intent": intent
        }

    def _query_knowledge_base(self, state: DialogueState) -> DialogueState:
        """Query RAG system for relevant information.

        Args:
            state: Current dialogue state

        Returns:
            Updated state with retrieved context
        """
        message = state["messages"][-1].content

        # Retrieve relevant documents
        docs = self.kb.query(message, top_k=3)

        # Add to context
        context = state["context"]
        context["retrieved_docs"] = [
            {"content": doc.page_content, "score": doc.metadata.get("score")}
            for doc in docs
        ]

        return {
            **state,
            "context": context
        }

    def _generate_response(self, state: DialogueState) -> DialogueState:
        """Generate natural language response.

        Args:
            state: Current dialogue state

        Returns:
            Updated state with AI response
        """
        message = state["messages"][-1].content
        context_docs = state["context"].get("retrieved_docs", [])

        # Build prompt with context
        context_text = "\n".join([
            f"- {doc['content']}" for doc in context_docs
        ])

        prompt = f"""You are a friendly Vietnamese restaurant receptionist.

Customer: {message}

Relevant Information:
{context_text}

Respond naturally in Vietnamese, being helpful and professional.

Response:"""

        response = self.llm.invoke(prompt)

        state["messages"].append(AIMessage(content=response.content))

        return state
```

**Key Features:**
- Fast inference for real-time performance
- Lightweight model for resource efficiency
- Quick avatar generation

### 3. Service Layer (src/services/)

**Purpose:** External service integrations and coordination

#### TTS Service
```python
# src/services/tts.py

class TTSService:

```python
# src/agents/reservation.py

from datetime import datetime, timedelta
from typing import List, Optional

class ReservationState(TypedDict):
    """Reservation agent state."""
    date: Optional[datetime]
    party_size: Optional[int]
    customer_name: Optional[str]
    phone: Optional[str]
    preferences: Dict[str, Any]
    available_tables: List[int]
    selected_table: Optional[int]
    status: str  # searching, holding, confirmed, failed

class ReservationAgent:
    """Handles table reservations and availability."""

    def __init__(self, db_connection):
        """Initialize reservation agent.

        Args:
            db_connection: Database connection for table operations
        """
        self.db = db_connection
        self.graph = self._build_graph()

    def _build_graph(self) -> StateGraph:
        """Build reservation workflow."""
        workflow = StateGraph(ReservationState)

        # Nodes
        workflow.add_node("validate_request", self._validate)
        workflow.add_node("check_availability", self._check_tables)
        workflow.add_node("suggest_alternatives", self._suggest_alternatives)
        workflow.add_node("hold_table", self._place_hold)
        workflow.add_node("confirm_booking", self._confirm_reservation)
        workflow.add_node("notify_staff", self._send_staff_notification)

        # Flow
        workflow.set_entry_point("validate_request")
        workflow.add_edge("validate_request", "check_availability")

        # Conditional: tables available or suggest alternatives
        workflow.add_conditional_edges(
            "check_availability",
            lambda s: "hold" if s["available_tables"] else "alternatives",
            {
                "hold": "hold_table",
                "alternatives": "suggest_alternatives"
            }
        )

        workflow.add_edge("hold_table", "confirm_booking")
        workflow.add_edge("confirm_booking", "notify_staff")

        return workflow.compile()

    async def create_reservation(
        self,
        date: datetime,
        party_size: int,
        customer_name: str,
        phone: str,
        preferences: Optional[Dict] = None
    ) -> ReservationResult:
        """Create new reservation.

        Args:
            date: Desired reservation datetime
            party_size: Number of guests
            customer_name: Customer name
            phone: Contact phone
            preferences: Optional preferences (seating, dietary)

        Returns:
            ReservationResult with status and details
        """
        state = ReservationState(
            date=date,
            party_size=party_size,
            customer_name=customer_name,
            phone=phone,
            preferences=preferences or {},
            available_tables=[],
            selected_table=None,
            status="searching"
        )

        # Run through reservation workflow
        result = await self.graph.ainvoke(state)

        return ReservationResult(
            success=result["status"] == "confirmed",
            reservation_id=result.get("reservation_id"),
            table_number=result.get("selected_table"),
            message=self._generate_message(result)
        )

    def _check_tables(self, state: ReservationState) -> ReservationState:
        """Check table availability.

        Args:
            state: Current reservation state

        Returns:
            Updated state with available tables
        """
        # Query database for available tables
        available = self.db.find_available_tables(
            date=state["date"],
            party_size=state["party_size"],
            duration_minutes=120
        )

        return {
            **state,
            "available_tables": [t.id for t in available]
        }

    def _suggest_alternatives(self, state: ReservationState) -> ReservationState:
        """Suggest alternative times/dates.

        Args:
            state: Current reservation state

        Returns:
            Updated state with alternatives
        """
        requested_date = state["date"]
        party_size = state["party_size"]

        # Check ±2 hours on same day
        alternatives = []
        for hour_delta in [-2, -1, 1, 2]:
            alt_time = requested_date + timedelta(hours=hour_delta)
            tables = self.db.find_available_tables(alt_time, party_size)
            if tables:
                alternatives.append({
                    "time": alt_time,
                    "tables": len(tables)
                })

        state["context"] = {
            "alternatives": alternatives,
            "original_request": requested_date
        }

        return state
```

**Supported TTS Engines:**
- EdgeTTS (Microsoft) - Default, free, multi-language
- FishTTS - Open source
- GPT-SoVITS - Voice cloning
- CosyVoice - High quality
- XTTS - Real-time synthesis

#### LLM Service
```python
# src/services/llm.py

class LLMService:

```python
# src/services/avatar/pipeline.py

class AvatarPipeline:
    """Avatar rendering and animation pipeline."""

    def __init__(self):
        """Initialize avatar components."""
        self.tts = CoquiTTS(model="xtts_v2")
        self.lipsync = LipSyncEngine()
        self.renderer = ThreeJSRenderer()

    async def generate_avatar_response(
        self,
        text: str,
        emotion: str = "neutral"
    ) -> AvatarResponse:
        """Generate animated avatar response.

        Args:
            text: Response text to speak
            emotion: Emotion for facial expression

        Returns:
            AvatarResponse with audio and animation data
        """
        # Text-to-Speech
        audio_bytes, phonemes = await self.tts.synthesize(
            text=text,
            language="vi",
            voice="vietnamese_female",
            return_phonemes=True
        )

        # Generate lip-sync visemes
        visemes = self.lipsync.phonemes_to_visemes(phonemes)

        # Generate animation data
        animation = self.renderer.create_animation(
            visemes=visemes,
            emotion=emotion,
            gestures=self._select_gestures(text)
        )

        return AvatarResponse(
            audio=audio_bytes,
            animation=animation,
            duration=len(audio_bytes) / SAMPLE_RATE
        )
```

**Key Features:**
- OpenAI API integration
- Conversation context management
- Response generation

#### WebRTC Service
```python
# src/services/webrtc.py

class WebRTCService:
    """WebRTC streaming and track management."""
```

**Key Features:**
- Real-time audio/video streaming
- Track management (audio, video)
- Connection state handling
- STUN/TURN server support

#### Real Service (Unified)
```python
# src/services/real.py

def build_real(opt, model=None, avatar=None):
    """Build Real implementation for selected model."""
```

**Key Features:**
- Model loading and caching
- Dynamic model selection
- Avatar management
- Warm-up optimization

### 4. Core Base Classes (src/core/)

#### BaseReal
```python
# src/core/base_real.py

class BaseReal(ABC):
    """Abstract base class for all AI models."""

    @abstractmethod
    def prepare_material(self, avatar_id: str):
        """Prepare avatar materials."""

    @abstractmethod
    def process_frame(self, audio_chunk):
        """Process audio and generate video frame."""
```

**Purpose:** Provides unified interface for all AI models

#### BaseASR
```python
# src/core/asr_base.py

class BaseASR(ABC):
    """Abstract base class for speech recognition."""
```

**Purpose:** Standard interface for ASR implementations

### 5. Web Interface (web/)

**Components:**
- `dashboard.html` - Main control panel
- `webrtcapi.html` - WebRTC API interface
- `client.js` - WebRTC client implementation

**Features:**
- Real-time avatar display
- Audio/video controls
- Chat interface
- Connection management

## Technology Stack

### Current Implementation

| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| **AI Models** | Wav2Lip, MuseTalk, Ultralight | Latest | Lip-sync & animation |
| **TTS** | EdgeTTS, FishTTS, XTTS | Latest | Text-to-speech |
| **LLM** | OpenAI API (optional) | Latest | Conversation |
| **Backend** | FastAPI | 0.109+ | REST & WebSocket API |
| **WebRTC** | aiortc | 1.5+ | Real-time streaming |
| **Frontend** | HTML/JS/CSS | - | Web interface |
| **ML Framework** | PyTorch | 2.7.1+ | Model inference |
| **Video Processing** | OpenCV | 4.12+ | Image/video manipulation |
| **Audio** | librosa, soundfile | Latest | Audio processing |

### Infrastructure

```yaml
Development:
  - Python 3.10+ virtual environment
  - Local GPU (NVIDIA with CUDA)
  - Direct Python execution

Production:
  - Docker containers
  - NVIDIA GPU support
  - systemd services
  - NGINX reverse proxy
```

## Current Implementation

### Project Structure

```
Digital-Human/
├── app.py                     # Main FastAPI application
├── src/
│   ├── api/
│   │   └── server.py          # API endpoint handlers
│   ├── core/
│   │   ├── real_base.py       # Base class for lip-sync models
│   │   └── asr_base.py        # Base class for ASR
│   ├── modules/
|   |
│   ├── services/
│   │   ├── real.py            # Lip-sync service manager
│   │   ├── tts.py             # TTS service implementations
│   │   ├── llm.py             # LLM service (OpenAI / Artrophic / Google / Local)
│   │   └── webrtc.py          # WebRTC service
│   └── utils/
│       └── logger.py          # Logging configuration
├── web/
│   ├── dashboard.html         # Main web interface
│   ├── webrtcapi.html         # WebRTC interface
│   └── client.js              # WebRTC client
├── data/
│   └── avatars/               # Avatar configurations
├── scripts/                   # Launch scripts
└── checkpoints/               # Model checkpoints
```

### Request Flow

1. **Client Connection** → WebRTC connection established to FastAPI server
2. **Audio Input** → Client sends audio via WebRTC data channel
3. **Text Processing** → Text converted to speech via TTS service
4. **Avatar Generation** → Selected AI model generates lip-sync video
5. **Response Streaming** → Animated avatar streamed back via WebRTC

### Session Management

```python
# Session lifecycle
1. Create session → FastAPI assigns session ID
2. WebRTC connection → Establish audio/video tracks
3. Model loading → Load/cache selected AI model
4. Processing → Handle text/audio requests
5. Response generation → Generate and stream avatar
6. Cleanup → Release resources on disconnect
```

## Future Enhancements

### Planned Enhancements (from Implementation Roadmap)

**Phase 1: Agent System (Restaurant Assistant)**
- LangGraph agent orchestration
- Dialogue agent with RAG (Qdrant)
- Reservation agent with table management
- vLLM server for Vietnamese LLM (Qwen2.5-7B)
- Whisper STT for speech recognition
- PostgreSQL for reservations, Redis for sessions

**Phase 2: Advanced Features**
- Multi-turn conversation memory
- Context-aware responses
- Emotion detection and adaptive behavior
- Advanced lip-sync with emotion mapping
- Multi-language support enhancements

**Phase 3: Production Features**
- Monitoring and analytics (Prometheus, Grafana)
- Load balancing and scaling
- Advanced session management
- Staff integration features
- Customer history and preferences


### Performance Targets (Future)

When agent system is implemented:

```
Target Latency: <2000ms (voice → voice)

Perception Pipeline:    500ms
  ├─ VAD:               50ms
  ├─ Whisper STT:      450ms

Agent Processing:       800ms
  ├─ Intent Class:     100ms
  ├─ vLLM Inference:   500ms
  ├─ RAG Query:        200ms

Avatar Pipeline:        700ms
  ├─ TTS:              400ms
  ├─ Lip Sync:         100ms
  ├─ Rendering:        200ms

Total:                 2000ms
```

**Target Throughput:**
- Concurrent sessions: 5-10 per GPU
- Requests/second: 10-20
- Database queries: <50ms p95
- 90%+ Vietnamese speech recognition accuracy

## Next Steps

1. ✅ Understand current architecture
2. 🔧 Set up [environment](./environment-setup.md)
3. 💻 Start [development](./development.md) (follow 4-week sprint plan)
4. 🚀 Follow [deployment guide](./deployment.md)
5. 📚 Reference [API docs](./api-reference.md)

## References

### Documentation
- [Environment Setup](./environment-setup.md)
- [Development Guide](./development.md)
- [Deployment Guide](./deployment.md)
- [API Reference](./api-reference.md)
- [Git Workflow](./branch-rule.md)


### External Resources
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [PyTorch Documentation](https://pytorch.org/docs/)
- [aiortc Documentation](https://aiortc.readthedocs.io/)
- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/) (for future agent implementation)

