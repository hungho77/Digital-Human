# Digital Human - Real-time AI Avatar

[![Pylint](https://github.com/hungho77/Digital-Human/actions/workflows/pylint.yml/badge.svg)](https://github.com/hungho77/Digital-Human/actions/workflows/pylint.yml)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![Code style: pylint](https://img.shields.io/badge/code%20style-pylint-blue)](https://pylint.pycqa.org/)

A real-time digital human platform with AI-powered lip-sync animation, voice synthesis, and WebRTC streaming. Built for Vietnamese market with support for multi-language conversation agents.

## ✅ Current Status

**IN ACTIVE DEVELOPMENT** - Core infrastructure completed, agent system in progress:
- ✅ **WebRTC Streaming**: Real-time video/audio streaming infrastructure
- ✅ **Service Architecture**: Modular service layer with TTS, LLM, and lip-sync
- ✅ **Session Management**: Multi-session support
- ✅ **Web Interface**: Dashboard and API endpoints
- ⏳ **AI Lip-sync**: SyncTalk model integration in progress
- ⏳ **Avatar System**: Configurable avatar rendering pipeline
- ⏳ **Agent System**: LangGraph-based dialogue and reservation agents
- ⏳ **RAG System**: Vietnamese knowledge base with vector database

## ✨ Features

### Current
- **Real-time Streaming**: WebRTC-based video/audio streaming
- **Service Layer**: Modular TTS, LLM, and lip-sync services
- **Web Interface**: Dashboard and WebRTC API endpoints
- **Multi-session Support**: Concurrent user handling

### In Development (4-Week Sprint)
- **AI Lip-sync**: SyncTalk for high-quality facial animation
- **Avatar System**: Configurable avatars and expressions
- **Speech Recognition**: Whisper for Vietnamese ASR
- **TTS**: ZipVoice for fast, high-quality Vietnamese speech
- **Vietnamese LLM**: vLLM + Qwen3-8B for local inference
- **Agent System**: LangGraph orchestration with dialogue and reservation agents
- **RAG System**: Qdrant vector database for knowledge retrieval

## 🏗️ Architecture

### System Overview
```
Digital-Human/
├── app.py                     # Main FastAPI application
├── src/
│   ├── api/
│   │   └── server.py          # API endpoint handlers
│   ├── core/
│   │   ├── real_base.py       # Base class for lip-sync models
│   │   └── asr_base.py        # Base class for ASR
│   ├── modules/               # AI modules
|   |
│   ├── services/
│   │   ├── real.py            # Lip-sync service manager
│   │   ├── tts.py             # TTS service implementations
│   │   ├── llm.py             # LLM service (OpenAI | Anthropic | Google | Local)
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

### 🎙️ **TTS Services**
- **ZipVoice** - Fast and high-quality zero-shot TTS (Primary for Vietnamese)
- **EdgeTTS** - Microsoft TTS, multiple languages
- **FishTTS** - Open source TTS
- **GPT-SoVITS** - Voice cloning TTS
- **CosyVoice** - High quality TTS
- **XTTS** - Real-time TTS

## 🚀 Quick Start

### 1. Prerequisites

**Hardware Requirements:**
- GPU: NVIDIA with 8GB+ VRAM (recommended: RTX 3060 or better)
- RAM: 16GB+ system memory
- Storage: 20GB+ for models and checkpoints

**Software Requirements:**
- Python 3.10+
- CUDA 12.1+ (for GPU acceleration)
- FFmpeg

### 2. Installation

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/Digital-Human.git
cd Digital-Human

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Download Models

```bash
# Download model checkpoints (instructions in docs/environment-setup.md)
# - SyncTalk model for lip-sync
# - Whisper model for ASR
# - ZipVoice model for TTS
# - Qwen3-8B model for LLM
```

### 4. Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit .env file with your settings:
# - LLM API keys (if using cloud services)
# - Database URLs (PostgreSQL, Redis, Qdrant)
# - TTS service configurations
```

### 5. Run the Application

#### Development Mode
```bash
# Start the application
python app.py --avatar_id avator_1

# The server will start on http://localhost:8010
```

#### Docker Deployment (Production)
```bash
# Using Docker Compose
docker-compose up -d

# Or build and run manually
docker build -t digital-human .
docker run -p 8010:8010 --gpus all digital-human
```

### 6. Access the Interface

- **Main Dashboard**: http://localhost:8010/dashboard.html
- **WebRTC API**: http://localhost:8010/webrtcapi.html
- **API Documentation**: http://localhost:8010/docs

### 7. Start Interaction

1. Open the dashboard in your browser
2. Click **"Start Connection"** to initiate WebRTC streaming
3. Wait for the avatar to appear
4. Use the chat interface to interact with the Digital Human

## Configuration Options

### Application Settings

```bash
# Avatar configuration
--avatar_id avator_1          # Avatar in data/avatars/ directory

# Server settings
--listenport 8010             # Server port (default: 8010)
--max_session 5               # Max concurrent sessions

# Transport method
--transport webrtc            # webrtc/rtcpush/virtualcam
```

### Service Configuration (via .env or command line)

**TTS Service:**
```bash
TTS_SERVICE=zipvoice           # zipvoice/edgetts/fishtts/xtts/etc.
TTS_SERVER=http://localhost:9880
TTS_VOICE_ID=default
```

**LLM Service:**
```bash
LLM_PROVIDER=local             # local/openai/anthropic/google
LLM_MODEL=Qwen3-8B-Instruct
LLM_API_BASE=http://localhost:8000/v1
OPENAI_API_KEY=your-key        # If using cloud LLM
```

**ASR Service:**
```bash
ASR_MODEL=whisper-large-v3
ASR_LANGUAGE=vi                # Vietnamese
WHISPER_MODEL_PATH=checkpoints/whisper
```

**Vector Database (RAG):**
```bash
QDRANT_HOST=localhost
QDRANT_PORT=6333
QDRANT_COLLECTION=digital_human_knowledge
```

## Service Setup

### 1. TTS Service (ZipVoice - Recommended for Vietnamese)

```bash
# Start ZipVoice server
cd /path/to/zipvoice
python server.py --port 9880

# Configure in .env
TTS_SERVICE=zipvoice
TTS_SERVER=http://localhost:9880
TTS_VOICE_ID=vietnamese_female
```

### 2. LLM Service (vLLM + Qwen3-8B)

```bash
# Start vLLM server
vllm serve Qwen/Qwen3-8B-Instruct \
    --port 8000 \
    --gpu-memory-utilization 0.8

# Configure in .env
LLM_PROVIDER=local
LLM_MODEL=Qwen3-8B-Instruct
LLM_API_BASE=http://localhost:8000/v1
```

### 3. Vector Database (Qdrant)

```bash
# Start Qdrant server
docker run -p 6333:6333 -p 6334:6334 \
    -v $(pwd)/qdrant_storage:/qdrant/storage \
    qdrant/qdrant

# Configure in .env
QDRANT_HOST=localhost
QDRANT_PORT=6333
```

### 4. Alternative TTS Services

**EdgeTTS (Free, Cloud-based):**
```bash
TTS_SERVICE=edgetts
TTS_VOICE_ID=vi-VN-HoaiMyNeural  # Vietnamese voice
```

**XTTS (Local, High-quality):**
```bash
TTS_SERVICE=xtts
TTS_SERVER=http://localhost:9000
```

## API Endpoints

### REST API

**Session Management:**
```javascript
// Create new session
POST /api/v1/session/create
Response: { "session_id": "uuid", "avatar_id": "avator_1" }

// End session
POST /api/v1/session/end
Body: { "session_id": "uuid" }
```

**Chat & Interaction:**
```javascript
// Send text message
POST /api/v1/chat
Body: {
    "session_id": "uuid",
    "message": "Hello, I want to make a reservation",
    "interrupt": false
}
Response: {
    "response": "Sure, I can help with that...",
    "agent": "dialogue",
    "intent": "reservation_request"
}

// Send audio (speech-to-text)
POST /api/v1/audio
Content-Type: multipart/form-data
Body: audio file
Response: {
    "text": "Transcribed text",
    "intent": "detected_intent"
}
```

**Avatar Control:**
```javascript
// Get speaking status
GET /api/v1/status/{session_id}
Response: {
    "is_speaking": true,
    "current_text": "...",
    "queue_length": 2
}

// Interrupt current speech
POST /api/v1/interrupt
Body: { "session_id": "uuid" }
```

**Reservation API (In Development):**
```javascript
// Check availability
POST /api/v1/reservation/check
Body: {
    "date": "2025-12-25",
    "time": "19:00",
    "party_size": 4
}

// Create reservation
POST /api/v1/reservation/create
Body: {
    "customer_name": "Nguyen Van A",
    "phone": "+84901234567",
    "date": "2025-12-25",
    "time": "19:00",
    "party_size": 4,
    "notes": "Window seat preferred"
}
```

### WebSocket API

```javascript
// Connect to WebSocket
const ws = new WebSocket('ws://localhost:8010/ws/{session_id}');

// Receive real-time updates
ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    // data.type: "audio", "video", "text", "status"
    // data.content: actual content
};

// Send message
ws.send(JSON.stringify({
    type: "text",
    content: "Hello"
}));
```

### WebRTC API

See [web/webrtcapi.html](web/webrtcapi.html) for interactive WebRTC demo.

**Full API documentation**: http://localhost:8010/docs (when server is running)

## 📁 Project Structure

```
Digital-Human/
├── app.py                   # FastAPI application entry point
├── requirements.txt         # Python dependencies
├── .env.example             # Environment variables template
├── Dockerfile               # Docker container configuration
├── docker-compose.yml       # Docker Compose setup
├── .pylintrc                # Code quality configuration
├── mypy.ini                 # Type checking configuration
├── .pre-commit-config.yaml  # Pre-commit hooks
├── src/
│   ├── api/                 # API layer
│   │   └── server.py        # FastAPI route handlers
│   ├── core/                # Core interfaces
│   │   ├── real_base.py     # Base class for lip-sync models
│   │   └── asr_base.py      # Base class for ASR
|   ├── modules/             # AI modules
│   ├── services/            # Service layer
│   │   ├── real.py          # Lip-sync service manager
│   │   ├── tts.py           # TTS service implementations
│   │   ├── llm.py           # LLM service (OpenAI/Anthropic/Google/Local)
│   │   └── webrtc.py        # WebRTC streaming service
│   ├── agents/              # LangGraph agents (in development)
│   │   ├── orchestrator.py  # Main orchestrator agent
│   │   ├── dialogue.py      # Dialogue agent
│   │   └── reservation.py   # Reservation agent
│   ├── rag/                 # RAG system (in development)
│   │   ├── vectorstore.py   # Qdrant integration
│   │   └── retriever.py     # Knowledge retrieval
│   └── utils/               # Utilities
│       └── logger.py        # Logging configuration
├── web/                     # Frontend
│   ├── dashboard.html       # Main dashboard
│   ├── webrtcapi.html       # WebRTC API interface
│   └── client.js            # WebRTC client
├── data/
│   └── avatars/             # Avatar configurations and assets
├── checkpoints/             # Model checkpoints
│   ├── synctalk/            # SyncTalk lip-sync model
│   ├── whisper/             # Whisper ASR model
│   ├── zipvoice/            # ZipVoice TTS model
│   └── qwen3/               # Qwen3 LLM model
├── scripts/                 # Utility scripts
│   ├── setup_dev.sh         # Development setup
│   ├── download_models.sh   # Model download script
│   └── deploy.sh            # Deployment script
├── docs/                    # Documentation
│   ├── environment-setup.md
│   ├── development.md
│   ├── architecture.md
│   ├── deployment.md
│   ├── api-reference.md
│   ├── branch-rule.md
│   └── documents.md
├── tests/                   # Test suite
│   ├── unit/                # Unit tests
│   ├── integration/         # Integration tests
│   └── conftest.py          # Pytest configuration
└── configs/                 # Configuration files
    └── avatar_config.yaml
```

## 🔧 Development

### Development Setup

```bash
# 1. Fork and clone the repository
git clone https://github.com/YOUR_USERNAME/Digital-Human.git
cd Digital-Human

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# 4. Install pre-commit hooks
pre-commit install

# 5. Run tests to verify setup
pytest tests/
```

### Code Quality Standards

This project follows strict code quality standards enforced through automated checks:

- ✅ **Google-style docstrings** - All functions must have proper documentation
- ✅ **Static typing** - Type hints for all function parameters and returns
- ✅ **Pylint score ≥ 7.0** - Code quality maintained through pylint
- ✅ **MyPy checks** - Static type checking passes
- ✅ **Bandit security scans** - No security vulnerabilities
- ✅ **Specific exception handling** - Avoid generic `Exception` catches
- ✅ **Pre-commit hooks** - Automated checks before commits
- ✅ **Test coverage ≥ 80%** - Comprehensive test suite

### Development Tools

| Tool | Purpose | Configuration |
|------|---------|---------------|
| **Pylint** | Code quality and style | `.pylintrc` |
| **MyPy** | Static type checking | `mypy.ini` |
| **Bandit** | Security scanning | `.bandit.yml` |
| **Pre-commit** | Git hooks | `.pre-commit-config.yaml` |
| **Pytest** | Testing framework | `pytest.ini` |
| **Black** | Code formatting | Line length 100 |

### Running Quality Checks

```bash
# Run all checks
make check

# Individual checks
make lint          # Pylint
make type-check    # MyPy
make security      # Bandit
make test          # Pytest

# Pre-commit hooks
pre-commit run --all-files
```

### 📚 Documentation

**Comprehensive guides in `docs/` folder:**

| Document | Description |
|----------|-------------|
| **[environment-setup.md](docs/environment-setup.md)** | Prerequisites, installation, model downloads |
| **[development.md](docs/development.md)** | 4-week sprint plan, team structure, workflow |
| **[architecture.md](docs/architecture.md)** | System design, components, technology stack |
| **[deployment.md](docs/deployment.md)** | Production deployment, Docker, monitoring |
| **[api-reference.md](docs/api-reference.md)** | REST API, WebSocket API, examples |
| **[branch-rule.md](docs/branch-rule.md)** | Git workflow, commit conventions, PR process |
| **[documents.md](docs/documents.md)** | Documentation overview and navigation |

### System Architecture

**Core Principles:**
- **Service-Oriented**: Modular services for TTS, LLM, ASR, lip-sync
- **Agent-Based**: LangGraph orchestration for multi-agent workflows
- **RAG-Enabled**: Vector database for knowledge retrieval
- **Real-time**: WebRTC streaming with low latency
- **Scalable**: Multi-session support with async processing
- **Vietnamese-First**: Optimized for Vietnamese language and market

**Technology Stack:**
- **Backend**: FastAPI, Python 3.10+, asyncio
- **AI Models**: SyncTalk, Whisper, ZipVoice, Qwen3-8B
- **LLM Serving**: vLLM for efficient inference
- **Vector DB**: Qdrant for RAG
- **Agents**: LangGraph for orchestration
- **Database**: PostgreSQL, Redis
- **Streaming**: WebRTC (aiortc)

## 🐛 Troubleshooting

### Common Issues

1. **Import Errors**
   ```bash
   # Ensure you're in the project root
   cd Digital-Human
   export PYTHONPATH="${PYTHONPATH}:$(pwd)"

   # Verify virtual environment is activated
   source venv/bin/activate
   ```

2. **Model Loading Errors**
   ```bash
   # Check if checkpoints exist
   ls -lh checkpoints/

   # Download missing models
   ./scripts/download_models.sh

   # Verify model paths in .env
   grep MODEL .env
   ```

3. **WebRTC Connection Issues**
   - **"Connecting..." stuck**:
     - Check if server is running: `curl http://localhost:8010/`
     - Refresh browser (Ctrl+F5)
     - Check browser console for errors (F12)
   - **No video showing**:
     - Verify GPU availability: `nvidia-smi`
     - Check STUN server enabled in dashboard
     - Ensure avatar files exist in `data/avatars/`
   - **Browser compatibility**:
     - Use Chrome 90+ or Firefox 88+
     - Safari has limited WebRTC support
   - **HTTPS requirement**:
     - Some browsers require HTTPS for WebRTC
     - Use reverse proxy (nginx) for production

4. **Service Connection Issues**
   ```bash
   # Check TTS service
   curl http://localhost:9880/health

   # Check LLM service
   curl http://localhost:8000/v1/models

   # Check Qdrant
   curl http://localhost:6333/
   ```

5. **Database Connection Issues**
   ```bash
   # Verify PostgreSQL
   psql -h localhost -U user -d digital_human

   # Verify Redis
   redis-cli ping

   # Check Qdrant
   curl http://localhost:6333/collections
   ```

6. **Performance Issues**
   ```bash
   # Check GPU utilization
   nvidia-smi -l 1

   # Monitor system resources
   htop

   # Check service logs
   tail -f logs/app.log
   ```

7. **Port Conflicts**
   ```bash
   # Check if port is in use
   lsof -i :8010

   # Use different port
   python app.py --listenport 8011
   ```

### System Verification

```bash
# Check Python version
python --version  # Should be 3.10+

# Check CUDA availability
python -c "import torch; print(torch.cuda.is_available())"

# Check dependencies
pip list | grep -E "torch|transformers|fastapi|aiortc"

# Run tests
pytest tests/ -v
```

### Debug Mode

Enable detailed logging:
```bash
# Set log level in .env
LOG_LEVEL=DEBUG

# Run with verbose output
python app.py --debug

# Check logs
tail -f logs/app.log
tail -f logs/error.log
```

### Getting Help

- **Documentation**: Check [docs/](docs/) folder
- **Issues**: Open GitHub issue with:
  - Error messages and stack traces
  - System info (`python --version`, `nvidia-smi`)
  - Configuration files (redact sensitive data)
  - Steps to reproduce
- **Community**: See CONTRIBUTING.md for support channels

## 🤝 Contributing

We welcome contributions! This project is under active development with a 4-week sprint plan.

### How to Contribute

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Follow code standards**: See [CONTRIBUTING.md](CONTRIBUTING.md)
4. **Write tests**: Maintain 80%+ coverage
5. **Run quality checks**: `make check`
6. **Commit with conventional format**: See [docs/branch-rule.md](docs/branch-rule.md)
7. **Push and create PR**

### Development Priorities

**Sprint Week 1-2: Core Infrastructure**
- ✅ Service architecture completed
- ⏳ SyncTalk lip-sync integration
- ⏳ Whisper ASR integration
- ⏳ ZipVoice TTS integration

**Sprint Week 3: Agent System**
- ⏳ LangGraph orchestrator
- ⏳ Dialogue agent with RAG
- ⏳ Reservation agent
- ⏳ Multi-turn conversation

**Sprint Week 4: Production Ready**
- ⏳ Performance optimization
- ⏳ Vietnamese knowledge base
- ⏳ Production deployment
- ⏳ Monitoring and logging

See [docs/development.md](docs/development.md) for detailed sprint plan.

### Areas for Contribution

- **AI Models**: Improve lip-sync quality, optimize inference
- **TTS Integration**: Add Vietnamese voice options
- **Agent System**: Enhance conversation flows
- **RAG System**: Expand knowledge base
- **Documentation**: Tutorials, examples, translations
- **Testing**: Increase coverage, add benchmarks
- **Performance**: Optimize latency, reduce resource usage

## 🗺️ Roadmap

### Phase 1: Core Infrastructure ✅ (Completed)
- [x] FastAPI web server
- [x] WebRTC streaming setup
- [x] Service layer architecture
- [x] Avatar rendering pipeline
- [x] Configuration management
- [x] Logging and monitoring

### Phase 2: AI Models Integration ⏳ (In Progress - Weeks 1-2)
- [ ] **SyncTalk** - High-quality lip-sync model
- [ ] **Whisper** - Vietnamese speech recognition
- [ ] **ZipVoice** - Vietnamese text-to-speech
- [ ] **vLLM** - Efficient LLM serving
- [ ] **Qwen3-8B** - Vietnamese language model

### Phase 3: Agent System ⏳ (Weeks 3-4)
- [ ] **Orchestrator Agent** - Session and workflow management
- [ ] **Dialogue Agent** - Conversation with RAG
- [ ] **Reservation Agent** - Table booking logic
- [ ] **RAG System** - Qdrant vector database
- [ ] **Memory System** - Multi-turn conversation context

### Phase 4: Production Ready 📅 (Future)
- [ ] Performance optimization (< 2s latency)
- [ ] Load testing (50+ concurrent users)
- [ ] Vietnamese knowledge base expansion
- [ ] Monitoring and alerting
- [ ] CI/CD pipeline
- [ ] Kubernetes deployment

### Phase 5: Advanced Features 📅 (Future)
- [ ] Multi-language support (English, Vietnamese, Chinese)
- [ ] Voice cloning for brand identity
- [ ] Emotion detection and response
- [ ] Custom avatar training
- [ ] Mobile app integration
- [ ] Analytics dashboard

## 📊 Current Status (December 2025)

**✅ Completed:**
- FastAPI backend with REST and WebSocket APIs
- WebRTC real-time streaming infrastructure
- Service architecture (TTS, LLM, ASR, lip-sync)
- Avatar rendering and configuration system
- Web interface (dashboard, WebRTC API)
- Documentation (environment, development, architecture, deployment, API, git workflow)
- Code quality standards (pylint, mypy, pre-commit hooks)
- Docker deployment support

**⏳ In Progress (4-Week Sprint):**
- SyncTalk lip-sync model integration
- Whisper ASR for Vietnamese
- ZipVoice TTS for Vietnamese
- vLLM + Qwen3-8B local LLM
- LangGraph agent orchestration
- Qdrant RAG system
- Reservation agent logic

**📅 Planned:**
- Production optimization
- Load balancing and scaling
- Advanced conversation flows
- Analytics and monitoring
- Mobile SDK

## 📄 License

Apache License 2.0 - See [LICENSE](LICENSE) file for details.

## 🔧 Technical Notes

### Technology Stack

**AI & ML:**
- **SyncTalk**: State-of-the-art lip-sync model
- **Whisper Large V3**: Multilingual speech recognition
- **ZipVoice**: Fast zero-shot TTS
- **Qwen3-8B**: Efficient Chinese-Vietnamese LLM
- **vLLM**: High-performance LLM serving

**Backend:**
- **FastAPI**: Modern Python web framework
- **aiortc**: WebRTC implementation
- **LangGraph**: Multi-agent orchestration
- **Qdrant**: Vector database for RAG

**Infrastructure:**
- **Docker**: Containerization
- **PostgreSQL**: Relational database
- **Redis**: Cache and message queue
- **NGINX**: Reverse proxy

### Performance Targets

| Metric | Target | Current Status |
|--------|--------|----------------|
| Response Latency | < 2s | ⏳ In Development |
| Lip-sync Quality | > 90% | ⏳ Testing |
| Concurrent Users | 50+ | ⏳ Optimization |
| GPU Memory | < 8GB | ⏳ Profiling |

### Vietnamese Market Optimization

- **Language Models**: Fine-tuned for Vietnamese
- **TTS Voices**: Natural Vietnamese speech
- **Knowledge Base**: Vietnamese restaurant domain
- **Cultural Context**: Vietnamese etiquette and preferences

### Dependency Compatibility

- **Python**: 3.10+ (tested on 3.10, 3.11)
- **PyTorch**: 2.0+ with CUDA 12.1+
- **Transformers**: 4.55.0+
- **FastAPI**: 0.115.0+
- **aiortc**: 1.13.0+

### Security & Privacy

- Environment variables for sensitive data
- Input validation and sanitization
- Rate limiting on API endpoints
- Secure WebRTC connections (DTLS)
- No data retention without consent
