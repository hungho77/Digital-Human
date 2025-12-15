# Development Guide

Comprehensive development guide for the Digital Human Restaurant Assistant system following the 4-week sprint implementation roadmap.

## Table of Contents

1. [Development Workflow](#development-workflow)
2. [Team Structure](#team-structure)
3. [Sprint Plan Overview](#sprint-plan-overview)
4. [Code Standards](#code-standards)
5. [Component Development](#component-development)
6. [Testing Strategy](#testing-strategy)
7. [Git Workflow](#git-workflow)

## Development Workflow

### Daily Development Cycle

```bash
# 1. Start your day
cd Digital-Human
source venv/bin/activate

# 2. Update codebase
git checkout develop
git pull origin develop

# 3. Create feature branch
git checkout -b feature/dialogue-agent-enhancement

# 4. Make changes
# ... development work ...

# 5. Run quality checks
make check

# 6. Run tests
make test

# 7. Commit and push
git add .
git commit -m "feat(agent): enhance dialogue context management"
git push origin feature/dialogue-agent-enhancement

# 8. Create Pull Request
```

### Development Time Allocation

Based on **4-Week Sprint Plan (2 People × 2h/day = 56 Total Hours)**:

| Week | Focus | Person A (Backend/Media) | Person B (Agent/RAG) |
|------|-------|-------------------------|---------------------|
| 1 | Foundation | Infrastructure & Voice | Agents & RAG |
| 2 | Integration | Avatar Enhancement | Advanced Conversation |
| 3 | Polish | Production Features | Business Logic |
| 4 | Deployment | System Integration | Optimization |

## Team Structure

### Person A: Senior AI Engineer (Backend/Media Specialist)

**Primary Responsibilities:**
- Backend architecture and orchestrator
- Voice processing (Whisper, TTS)
- Avatar generation and animation
- WebRTC streaming
- Performance optimization

**Tech Stack:**
- vLLM for LLM inference
- Faster-whisper for STT
- ZipVoice TTS for voice synthesis
- FastAPI for backend services

**Weekly Tasks:**
```yaml
Week 1:
  - vLLM integration and testing
  - Audio processing pipeline (Whisper + VAD)
  - TTS and basic avatar setup
  - WebRTC server for real-time communication

Week 2:
  - Avatar animation system
  - Lip-sync implementation
  - Voice quality enhancement
  - Real-time streaming optimization

Week 3:
  - Multi-language support
  - Advanced audio processing
  - Avatar customization
  - System monitoring setup

Week 4:
  - Production deployment
  - Monitoring and logging
  - Security hardening
  - Performance optimization
```

### Person B: Junior AI Engineer (Agent/RAG Specialist)

**Primary Responsibilities:**
- LangGraph agent development
- RAG system implementation
- Conversation logic and flows
- Knowledge base management
- Business logic integration

**Tech Stack:**
- LangGraph for agent orchestration
- LangChain for tools and chains
- Qdrant for vector database
- sentence-transformers for embeddings
- PostgreSQL for structured data

**Weekly Tasks:**
```yaml
Week 1:
  - LangGraph setup and agent architecture
  - RAG system foundation (Qdrant + embeddings)
  - Dialogue agent core logic
  - Reservation agent development

Week 2:
  - Advanced dialogue patterns
  - Reservation logic enhancement
  - RAG system enhancement
  - Agent coordination

Week 3:
  - Restaurant domain knowledge
  - Advanced conversation scenarios
  - Reservation intelligence
  - Staff integration features

Week 4:
  - Agent performance tuning
  - Comprehensive testing
  - Knowledge base optimization
  - Documentation and knowledge transfer
```

## Sprint Plan Overview

### Week 1: Foundation & Core Systems (14h each)

#### Day-by-Day Breakdown

**Day 1 (2h):**
- Person A: Docker compose + vLLM + FastAPI skeleton
- Person B: LangGraph setup + agent state schemas

**Day 2 (2h):**
- Person A: Whisper integration + VAD + audio endpoints
- Person B: RAG foundation (Qdrant + embeddings)

**Day 3 (2h):**
- Person A: Coqui TTS + Three.js + basic avatar
- Person B: Dialogue agent core logic

**Day 4 (2h):**
- Person A: Session management + WebSocket + Redis
- Person B: Reservation agent + table logic

**Day 5 (2h):**
- Person A: WebRTC audio capture + frontend basics
- Person B: RAG integration + knowledge retrieval

**Day 6 (2h):**
- Person A: End-to-end pipeline testing
- Person B: Agent tools development

**Day 7 (2h):**
- Person A: Orchestrator foundation
- Person B: LangGraph workflow integration

**Week 1 Target:** Working voice-to-agent-to-voice pipeline with basic reservation capability

### Week 2-4 Milestones

## Code Standards

### Python Code Quality

#### 1. Google-Style Docstrings

```python
def process_reservation(
    date: str,
    party_size: int,
    preferences: Optional[Dict[str, Any]] = None
) -> Tuple[bool, str, Optional[Dict]]:
    """Process restaurant reservation request.

    Checks table availability, applies business rules, and creates
    reservation if possible. Handles special dietary requirements
    and seating preferences.

    Args:
        date: Reservation date in ISO format (YYYY-MM-DD HH:MM)
        party_size: Number of guests (1-20)
        preferences: Optional dict with keys:
            - dietary: List of dietary restrictions
            - seating: Preferred seating area
            - occasion: Special occasion type

    Returns:
        Tuple of (success, message, reservation_details):
        - success: True if reservation created
        - message: Human-readable status message
        - reservation_details: Dict with booking info or None

    Raises:
        ValueError: If date is in the past or party_size invalid
        DatabaseError: If database connection fails

    Example:
        >>> success, msg, details = process_reservation(
        ...     "2025-12-20 19:00",
        ...     4,
        ...     {"dietary": ["vegetarian"], "seating": "window"}
        ... )
        >>> print(msg)
        'Reservation confirmed for 4 guests at 7:00 PM'
    """
    if party_size < 1 or party_size > 20:
        raise ValueError(f"Invalid party size: {party_size}")

    # Implementation...
    return True, "Reservation confirmed", {"id": 123}
```

#### 2. Type Hints

```python
from typing import Dict, List, Optional, Tuple, Any, Union
from datetime import datetime
from pydantic import BaseModel

# Use Pydantic for complex types
class ReservationRequest(BaseModel):
    """Restaurant reservation request model."""
    date: datetime
    party_size: int
    customer_name: str
    phone: str
    preferences: Optional[Dict[str, Any]] = None

# Type aliases for clarity
TableID = int
SessionID = str
AgentState = Dict[str, Any]

def find_available_tables(
    date: datetime,
    party_size: int,
    duration_minutes: int = 120
) -> List[Tuple[TableID, str]]:
    """Find available tables for given criteria."""
    pass
```

#### 3. Exception Handling

```python
from src.exceptions import (
    TableNotAvailableError,
    InvalidReservationError,
    DatabaseError
)

def create_reservation(request: ReservationRequest) -> Reservation:
    """Create new reservation with proper error handling."""
    try:
        # Validate request
        validate_reservation_request(request)

    except InvalidReservationError as e:
        logger.error(f"Invalid reservation request: {e}")
        raise  # Re-raise for caller to handle

    except ValueError as e:
        logger.error(f"Validation error: {e}")
        raise InvalidReservationError(f"Invalid input: {e}") from e

    try:
        # Database operations
        tables = find_available_tables(request.date, request.party_size)
        if not tables:
            raise TableNotAvailableError("No tables available")

        reservation = db.create_reservation(request, tables[0])

    except DatabaseError as e:
        logger.critical(f"Database error creating reservation: {e}")
        raise  # Critical error, propagate up

    except Exception as e:
        # Unexpected error - log and convert to known type
        logger.exception(f"Unexpected error in create_reservation: {e}")
        raise DatabaseError("Failed to create reservation") from e

    return reservation
```

### LangGraph Agent Development

#### Agent Structure

```python
from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage, AIMessage
from typing import TypedDict, Annotated

# Define agent state
class DialogueState(TypedDict):
    """State for dialogue agent."""
    messages: List[Union[HumanMessage, AIMessage]]
    customer_name: Optional[str]
    intent: Optional[str]
    context: Dict[str, Any]
    reservation_details: Optional[Dict]

# Create agent graph
workflow = StateGraph(DialogueState)

# Define nodes
def understand_intent(state: DialogueState) -> DialogueState:
    """Extract intent from customer message.

    Args:
        state: Current dialogue state

    Returns:
        Updated state with intent classification
    """
    last_message = state["messages"][-1].content
    intent = classify_intent(last_message)

    return {
        **state,
        "intent": intent
    }

def route_to_agent(state: DialogueState) -> str:
    """Route to appropriate specialized agent.

    Args:
        state: Current dialogue state

    Returns:
        Next node name to execute
    """
    intent = state["intent"]

    if intent == "reservation":
        return "reservation_agent"
    elif intent in ["menu", "faq"]:
        return "rag_agent"
    else:
        return "general_dialogue"

# Build graph
workflow.add_node("understand_intent", understand_intent)
workflow.add_node("reservation_agent", handle_reservation)
workflow.add_node("rag_agent", handle_rag_query)
workflow.add_node("general_dialogue", handle_general)

# Add edges with routing
workflow.set_entry_point("understand_intent")
workflow.add_conditional_edges(
    "understand_intent",
    route_to_agent,
    {
        "reservation_agent": "reservation_agent",
        "rag_agent": "rag_agent",
        "general_dialogue": "general_dialogue"
    }
)

# Compile
dialogue_agent = workflow.compile()
```

### RAG System Development

```python
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import Qdrant
from langchain.chains import RetrievalQA
from qdrant_client import QdrantClient

class RestaurantKnowledgeBase:
    """RAG system for restaurant information."""

    def __init__(self, qdrant_url: str, collection_name: str):
        """Initialize knowledge base.

        Args:
            qdrant_url: Qdrant server URL
            collection_name: Collection name for restaurant data
        """
        self.client = QdrantClient(url=qdrant_url)
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
        self.vectorstore = Qdrant(
            client=self.client,
            collection_name=collection_name,
            embeddings=self.embeddings
        )

    def query(
        self,
        question: str,
        top_k: int = 3,
        filter_dict: Optional[Dict] = None
    ) -> List[Document]:
        """Query knowledge base with semantic search.

        Args:
            question: Natural language question
            top_k: Number of results to return
            filter_dict: Optional metadata filters

        Returns:
            List of relevant documents with scores
        """
        # Semantic search
        docs = self.vectorstore.similarity_search_with_score(
            question,
            k=top_k,
            filter=filter_dict
        )

        return docs

    def ingest_documents(
        self,
        documents: List[Dict[str, Any]]
    ) -> None:
        """Ingest restaurant documents into knowledge base.

        Args:
            documents: List of dicts with 'text' and 'metadata'
        """
        from langchain.docstore.document import Document

        docs = [
            Document(
                page_content=doc["text"],
                metadata=doc.get("metadata", {})
            )
            for doc in documents
        ]

        self.vectorstore.add_documents(docs)
```

## Component Development

### 1. Voice Pipeline Development

```bash
# Location: src/services/perception/
├── audio_capture.py      # WebRTC audio capture
├── vad.py                # Voice Activity Detection
├── whisper_stt.py        # Speech-to-Text
└── audio_preprocessor.py # Noise reduction, normalization
```

**Key Implementation:**

```python
from faster_whisper import WhisperModel
import torch

class WhisperSTT:
    """Fast Whisper speech-to-text service."""

    def __init__(
        self,
        model_size: str = "large-v3",
        device: str = "cuda",
        compute_type: str = "float16"
    ):
        """Initialize Whisper model.

        Args:
            model_size: Model size (tiny, base, small, medium, large-v3)
            device: Device to run on (cuda/cpu)
            compute_type: Computation precision
        """
        self.model = WhisperModel(
            model_size,
            device=device,
            compute_type=compute_type
        )

    async def transcribe(
        self,
        audio_bytes: bytes,
        language: str = "vi"
    ) -> Tuple[str, float]:
        """Transcribe audio to text.

        Args:
            audio_bytes: Raw audio data
            language: Language code (vi for Vietnamese)

        Returns:
            Tuple of (transcribed_text, confidence_score)
        """
        segments, info = self.model.transcribe(
            audio_bytes,
            language=language,
            beam_size=5,
            vad_filter=True
        )

        text = " ".join([segment.text for segment in segments])
        confidence = info.language_probability

        return text.strip(), confidence
```

### 2. Agent Development

See [architecture.md](./architecture.md) for complete agent architecture.

### 3. Avatar Rendering

```bash
# Location: src/services/avatar/
├── avatar_renderer.py     # Three.js rendering
├── lipsync.py            # Phoneme-to-viseme mapping
├── animation_controller.py # Gesture and expression
└── models/               # 3D avatar models (VRM/GLB)
```

## Testing Strategy

### Unit Tests

```python
# tests/test_agents/test_reservation_agent.py
import pytest
from src.agents.reservation import ReservationAgent
from datetime import datetime, timedelta

class TestReservationAgent:
    """Test suite for reservation agent."""

    @pytest.fixture
    def agent(self):
        """Create reservation agent instance."""
        return ReservationAgent(config=test_config)

    def test_find_available_tables_success(self, agent):
        """Test finding available tables for valid request."""
        tomorrow = datetime.now() + timedelta(days=1)
        tomorrow_7pm = tomorrow.replace(hour=19, minute=0)

        tables = agent.find_available_tables(
            date=tomorrow_7pm,
            party_size=4
        )

        assert len(tables) > 0
        assert all(t.capacity >= 4 for t in tables)

    def test_reservation_past_date_raises_error(self, agent):
        """Test that past dates raise ValueError."""
        yesterday = datetime.now() - timedelta(days=1)

        with pytest.raises(ValueError, match="past"):
            agent.find_available_tables(
                date=yesterday,
                party_size=4
            )

    @pytest.mark.asyncio
    async def test_create_reservation_full_flow(self, agent):
        """Test complete reservation creation flow."""
        request = ReservationRequest(
            date=datetime.now() + timedelta(days=2),
            party_size=4,
            customer_name="Nguyen Van A",
            phone="0901234567"
        )

        result = await agent.create_reservation(request)

        assert result.success is True
        assert result.reservation_id is not None
        assert "confirmed" in result.message.lower()
```

### Integration Tests

```python
# tests/test_integration/test_voice_to_agent.py
import pytest
from src.services.orchestrator import Orchestrator

@pytest.mark.integration
class TestVoiceToAgentPipeline:
    """Test end-to-end voice processing pipeline."""

    @pytest.fixture
    async def orchestrator(self):
        """Create orchestrator with all services."""
        orch = Orchestrator()
        await orch.initialize()
        yield orch
        await orch.cleanup()

    @pytest.mark.asyncio
    async def test_full_reservation_flow(self, orchestrator):
        """Test complete flow from voice to reservation."""
        # Simulate audio input
        audio_file = "tests/fixtures/reservation_request_vi.wav"

        # Process through pipeline
        result = await orchestrator.process_audio(audio_file)

        # Verify pipeline stages
        assert result.transcript is not None
        assert result.intent == "reservation"
        assert result.agent_response is not None
        assert result.tts_audio is not None
```

### Performance Tests

```python
# tests/test_performance/test_latency.py
import pytest
import time

@pytest.mark.performance
class TestResponseLatency:
    """Test system response time requirements."""

    def test_voice_to_voice_under_2_seconds(self, orchestrator):
        """Verify <2s total response time."""
        audio_input = load_test_audio()

        start = time.time()
        response = orchestrator.process_audio(audio_input)
        end = time.time()

        latency = end - start
        assert latency < 2.0, f"Latency {latency}s exceeds 2s target"
```

## Git Workflow

### Branch Strategy

```
main (production)
  └── develop (integration)
       ├── feature/dialogue-agent-context
       ├── feature/rag-system-enhancement
       ├── feature/avatar-lipsync
       └── bugfix/whisper-timeout
```

### Commit Message Convention

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `style`: Code style (formatting)
- `refactor`: Code refactoring
- `perf`: Performance improvement
- `test`: Tests
- `chore`: Maintenance

**Examples:**

```
feat(agent): add multi-turn conversation memory

- Implement conversation history tracking
- Add context window management
- Support interruption handling

Implements #45
```

```
fix(whisper): resolve timeout on long audio files

Fixed timeout issue by implementing chunked processing
for audio files longer than 30 seconds.

Fixes #67
```

### Pull Request Process

1. **Create PR** with template
2. **CI Checks** must pass (pylint, mypy, tests)
3. **Code Review** by team lead
4. **Test** in staging environment
5. **Merge** to develop
6. **Deploy** to production (from main)

## Performance Optimization

### Profiling

```python
# Use cProfile for bottleneck detection
python -m cProfile -o profile.stats app.py

# Analyze with snakeviz
pip install snakeviz
snakeviz profile.stats
```

### Memory Optimization

```python
# Use torch.cuda.empty_cache() after batch processing
import torch

def process_batch(audio_batch):
    """Process audio batch with memory cleanup."""
    result = model.process(audio_batch)
    torch.cuda.empty_cache()
    return result
```

## Next Steps

1. ✅ Development environment setup
2. 📖 Review [architecture.md](./architecture.md) for system design
3. 🚀 Start Week 1 tasks from sprint plan
4. 📊 Track progress in project management tool
5. 🧪 Write tests alongside features

## References

- [System Architecture](./architecture.md)
- [API Reference](./api-reference.md)
- [Deployment Guide](./deployment.md)

