# Documentation Overview

Comprehensive documentation for the Digital Human Restaurant Assistant project.

## 📚 Documentation Structure

### Essential Documentation (6 Core Files)

| Document | Description | Size | Lines |
|----------|-------------|------|-------|
| **[environment-setup.md](./environment-setup.md)** | Complete environment setup guide | 13KB | ~615 |
| **[development.md](./development.md)** | Development workflow & 4-week sprint plan | 19KB | ~769 |
| **[architecture.md](./architecture.md)** | System architecture & components | 29KB | ~824 |
| **[deployment.md](./deployment.md)** | Deployment strategies & production setup | 19KB | ~921 |
| **[api-reference.md](./api-reference.md)** | Complete API documentation | 17KB | ~976 |
| **[branch-rule.md](./branch-rule.md)** | Git workflow & commit conventions | 13KB | ~609 |


## 🎯 Quick Navigation

### For New Developers

1. Start here: **[environment-setup.md](./environment-setup.md)**
   - Prerequisites & system requirements
   - Software installation
   - Model downloads
   - Database setup

2. Then read: **[development.md](./development.md)**
   - Development workflow
   - Team structure (2 people × 2h/day)
   - Week-by-week sprint plan
   - Code standards

3. Understand: **[architecture.md](./architecture.md)**
   - System overview
   - Component interactions
   - Agent architecture (LangGraph)
   - Technology stack

### For DevOps Engineers

1. **[deployment.md](./deployment.md)**
   - Development vs Production setup
   - Docker deployment
   - Kubernetes (optional)
   - Monitoring & maintenance

### For API Developers

1. **[api-reference.md](./api-reference.md)**
   - REST API endpoints
   - WebSocket API
   - Agent API
   - Request/Response examples

### For Everyone

1. **[branch-rule.md](./branch-rule.md)**
   - Git branch strategy
   - Commit message format
   - Pull request process
   - Code review guidelines

## 📋 Documentation Summary

### Key Features

✅ **Environment Setup**
- Hardware requirements (GPU specs)
- Software installation (Python, CUDA, Docker)
- Model downloads (vLLM, Whisper, TTS)
- Database configuration (PostgreSQL, Redis, Qdrant)

✅ **Development Guide**
- 4-week sprint plan (56 hours total)
- Team structure (2 developers)
- Person A: Backend/Media (vLLM, Whisper, TTS, Avatar)
- Person B: Agent/RAG (LangGraph, Qdrant, Embeddings)
- Code standards (Google docstrings, type hints)

✅ **Architecture Documentation**
- High-level system diagram
- Perception Pipeline (WebRTC → VAD → Whisper)
- Orchestrator Agent (session management)
- Dialogue Agent (LangGraph + RAG)
- Reservation Agent (table management)
- Avatar Pipeline (TTS → Lip-sync → Three.js)

✅ **Deployment Strategies**
- Development (local, single machine)
- Production (systemd services, NGINX)
- Docker Compose (containerized)
- Kubernetes (scalable, optional)
- Monitoring (Prometheus, Grafana)

✅ **Complete API Reference**
- REST API (sessions, conversations, reservations)
- WebSocket API (real-time audio/video)
- Agent API (dialogue, reservation agents)
- Rate limiting, error handling
- Python & JavaScript SDK examples

✅ **Git Workflow**
- Branch strategy (main → develop → feature)
- Conventional commits format
- Pull request process
- Code review guidelines
- Release process

## 🏗️ Architecture Highlights

### System Components

```
Customer Interface (WebRTC)
        ↓
Perception Pipeline (Whisper + VAD)
        ↓
Orchestrator Agent (LangGraph)
     ↙     ↘
Dialogue   Reservation
 Agent      Agent
   ↓          ↓
 RAG      Tables DB
        ↓
Avatar Pipeline (TTS + Three.js)
        ↓
Customer Interface
```

### Technology Stack

**AI/ML:**
- vLLM + Qwen2.5-7B-Instruct (Vietnamese LLM)
- faster-whisper (Speech-to-Text)
- Coqui TTS XTTS-v2 (Text-to-Speech)
- silero-vad (Voice Activity Detection)
- sentence-transformers (Embeddings)

**Agents:**
- LangGraph (Agent orchestration)
- LangChain (Tools & chains)
- Qdrant (Vector database)

**Backend:**
- FastAPI (REST API)
- WebSocket (Real-time)
- PostgreSQL (Structured data)
- Redis (Cache & sessions)

**Frontend:**
- Three.js (Avatar rendering)
- WebRTC (Audio/video streaming)
- HTML/JS (Dashboard)

### Performance Targets

```
Total Latency: <2000ms (voice → voice)

Breakdown:
- Perception:  500ms (VAD + Whisper)
- Agent:       800ms (Intent + LLM + RAG)
- Avatar:      700ms (TTS + Lip-sync + Render)
```

## 🚀 Getting Started

### Quick Start (5 Minutes)

```bash
# 1. Clone repository
git clone https://github.com/YOUR_USERNAME/Digital-Human.git
cd Digital-Human

# 2. Install dependencies
pip install -r requirements.txt

# 3. Start application
python app.py

# 4. Access dashboard
# http://localhost:8010/dashboard.html
```

### Development Setup

For development with code quality tools:

```bash
# 1. Run automated setup
./scripts/setup_dev.sh

# 2. Or manually
pip install -r requirements.txt
pip install -r requirements-dev.txt
pre-commit install

# 3. Verify setup
./scripts/verify_setup.sh
```

### Full Setup (1-2 Hours)

Follow **[environment-setup.md](./environment-setup.md)** for complete setup including:
- GPU drivers & CUDA
- Model downloads
- Future: vLLM, Whisper, database setup (see Implementation Roadmap)

## 👥 Development Status

### Current Implementation (Completed)

✅ **Core Features:**
- FastAPI server with WebSocket support
- Three AI models (Wav2Lip, MuseTalk, Ultralight)
- WebRTC real-time streaming
- TTS integration (EdgeTTS and others)
- Web interface (dashboard + WebRTC API)
- Session management
- Modular architecture

✅ **Code Quality:**
- Pylint configuration (≥7.0 score)
- Pre-commit hooks
- Type hints and docstrings
- Testing framework setup

### Future Development (4-Week Sprint Plan)

See **[development.md](./development.md)** for detailed sprint plan:

**Person A: Backend/Media Specialist**
- Week 1: Voice pipeline (Whisper STT + VAD)
- Week 2: Avatar enhancement & lip-sync optimization
- Week 3: Production features & multi-language
- Week 4: Deployment & system integration

**Person B: Agent/RAG Specialist**
- Week 1: LangGraph agents + RAG foundation (Qdrant)
- Week 2: Advanced conversation & reservation logic
- Week 3: Business logic & restaurant knowledge base
- Week 4: Optimization & testing

**Target Deliverables:**
- Dialogue agent with context memory
- Reservation agent with table management
- RAG knowledge base (100+ Q&As)
- vLLM server for Vietnamese LLM
- <2s voice-to-voice latency

## 📊 Project Status

### Completed ✅

- ✅ WebRTC real-time streaming
- ✅ Web interface (dashboard + API)
- ✅ Session management
- ✅ Modular architecture
- ✅ Code quality tools (pylint, mypy, pre-commit)
- ✅ Docker deployment
- ✅ Comprehensive documentation

### In Progress / Future (4-Week Sprint)
- ⏳ Lipsync model (Synctalk)
- ⏳ Speech-to-text (Whisper integration)
- ⏳ Text-to-speech (Zipvoice integration)
- ⏳ Vietnamese LLM (vLLM + Qwen3-8B)
- ⏳ Agent system (LangGraph orchestration)
- ⏳ RAG system (Qdrant vector database)
- ⏳ Reservation system (table management)
- ⏳ Multi-turn conversation memory
- ⏳ Restaurant knowledge base

### Success Criteria (Sprint Goals)

**Technical Achievements:**
- <2 second response time (voice → voice)
- 90%+ Vietnamese speech recognition accuracy
- Natural lip-sync and facial expressions
- Successful table reservations end-to-end
- Multi-turn conversation memory
- Restaurant knowledge base with 100+ Q&As

**Business Value:**
- Handle 5+ common restaurant scenarios
- Professional appearance for customer-facing use
- Staff management interface
- Scalable architecture

## 🔗 Related Documentation

### Project Root Documentation

- [README.md](../README.md) - Project overview & quick start
- [CONTRIBUTING.md](../CONTRIBUTING.md) - Contribution guidelines
- [DOCKER.md](../DOCKER.md) - Docker deployment guide
- [AGENTS.md](../AGENTS.md) - Documentation index
- [REFACTORING_SUMMARY.md](../REFACTORING_SUMMARY.md) - Architecture refactoring notes

### Configuration Files

- `.pylintrc` - Code quality configuration
- `.pre-commit-config.yaml` - Pre-commit hooks
- `.editorconfig` - Editor consistency
- `docker-compose.yml` - Docker services
- `Makefile` - Build automation

## 📞 Support

### For Questions

- **Setup Issues**: See [environment-setup.md](./environment-setup.md) troubleshooting
- **Development**: Check [development.md](./development.md)
- **API Usage**: Review [api-reference.md](./api-reference.md)
- **Deployment**: Follow [deployment.md](./deployment.md)

### Contact

- **GitHub Issues**: Report bugs and feature requests
- **Discussions**: Ask questions and share ideas
- **Email**: support@example.com
- **Discord**: Join our community

## 🎓 Learning Path

### Beginner (Week 1)

1. Read [environment-setup.md](./environment-setup.md)
2. Setup development environment
3. Run the application locally
4. Explore the dashboard

### Intermediate (Week 2-3)

1. Read [development.md](./development.md)
2. Understand sprint plan structure
3. Study code standards & examples
4. Make first contribution

### Advanced (Week 4)

1. Read [architecture.md](./architecture.md)
2. Understand agent workflows
3. Customize agents & RAG
4. Optimize performance

### Production (Ongoing)

1. Read [deployment.md](./deployment.md)
2. Setup production environment
3. Configure monitoring
4. Maintain & scale

## 📝 Documentation Quality

### Completeness

- ✅ All major topics covered
- ✅ Step-by-step instructions
- ✅ Code examples included
- ✅ Troubleshooting sections
- ✅ References to external resources

### Accuracy

- ✅ Based on actual system architecture
- ✅ Tested commands and examples
- ✅ Version-specific information
- ✅ Performance metrics included

### Usability

- ✅ Clear structure with TOC
- ✅ Markdown formatting
- ✅ Syntax highlighting
- ✅ Cross-referenced documents
- ✅ Quick reference sections

