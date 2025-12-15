# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Common Development Commands

### Running the Application
```bash
# Start the main application with specific avatar
python app.py --avatar_id avator_1

# Development mode with debug logging
python app.py --avatar_id avator_1 --debug

# Specify port
python app.py --listenport 8011

# Use specific model (wav2lip, musetalk, ultralight)
python app.py --model wav2lip --avatar_id avator_1
```

### Code Quality & Linting

**Pylint** is the primary code quality tool for this project. All code must maintain a Pylint score ≥ 7.0.

```bash
# Run Pylint on all Python files
pylint $(git ls-files '*.py') --fail-under=7.0

# Run Pylint on specific file
pylint src/services/real.py

# Run Pylint with full report
pylint src/ --output-format=text --reports=yes --score=yes

# Check critical errors only (used in CI)
pylint $(git ls-files '*.py') --disable=all --enable=E,F --fail-under=9.0
```

**Important Pylint Configuration** (from `.pylintrc`):
- Max line length: 100 characters
- Disabled warnings: `C0111` (missing-docstring), `C0103` (invalid-name), `R0903` (too-few-public-methods), `R0913` (too-many-arguments), `W0212` (protected-access), `C0302` (too-many-lines)
- Good variable names: `i, j, k, ex, _, id, x, y, z, w, h, fp, fn`
- Maximum arguments: 10
- Maximum local variables: 20
- Maximum statements: 50

### Pre-commit Hooks
```bash
# Install pre-commit hooks
pre-commit install

# Run all pre-commit hooks manually
pre-commit run --all-files

# Update pre-commit hook versions
pre-commit autoupdate
```

### Testing
```bash
# Run all tests
pytest tests/

# Run specific test file
pytest tests/test_services.py

# Run with verbose output
pytest -v

# Run with coverage report
pytest --cov=src --cov-report=html
```

### Docker Deployment
```bash
# Build Docker image
docker build -t digital-human .

# Run with GPU support
docker run -p 8010:8010 --gpus all digital-human

# Using Docker Compose
docker-compose up -d

# View logs
docker-compose logs -f
```

## Architecture Overview

### Core Design Principles

**1. Modular AI Model System**
- Each AI model (Wav2Lip, MuseTalk, Ultralight) is implemented as a separate module in `src/modules/`
- All models inherit from `BaseReal` interface (`src/core/base_real.py`)
- Dynamic model loading prevents dependency conflicts - only the selected model's dependencies are loaded
- Model selection is done via `--model` CLI argument

**2. Service Layer Abstraction**
- Clean separation between TTS, LLM, WebRTC, and model services
- `src/services/real.py` acts as the unified service manager coordinating all AI models
- Service implementations are swappable (e.g., different TTS engines: EdgeTTS, FishTTS, XTTS)

**3. Real-time WebRTC Streaming**
- `src/services/webrtc.py` handles real-time audio/video streaming using `aiortc`
- Session management for multiple concurrent users
- Efficient GPU-accelerated model inference

### Key Components

**FastAPI Server (`app.py`)**
- Main application entry point
- REST API endpoints: `/api/chat`, `/api/audio`, `/api/record`, `/api/interrupt`
- WebSocket endpoint for real-time communication
- Session management and lifecycle handling

**AI Model Modules (`src/modules/`)**
- `musetalk/` - High-quality facial animation using diffusion model
- `wav2lip/` - Accurate lip-sync with face alignment
- `ultralight/` - Lightweight model for fast inference
- Each module contains: model code, avatar preparation, and inference logic

**Service Layer (`src/services/`)**
- `real.py` - Unified model loader and cache manager (`build_real()` function)
- `tts.py` - Text-to-speech service (EdgeTTS, FishTTS, GPT-SoVITS, CosyVoice, XTTS)
- `llm.py` - LLM integration (OpenAI, Anthropic, Google, Local)
- `webrtc.py` - WebRTC streaming and track management

**Core Interfaces (`src/core/`)**
- `base_real.py` - `BaseReal` abstract class defining standard interface for all models
- `asr_base.py` - `BaseASR` abstract class for speech recognition implementations

**Web Interface (`web/`)**
- `dashboard.html` - Main control panel
- `webrtcapi.html` - WebRTC API testing interface
- `client.js` - WebRTC client implementation

### Data Flow

1. **Client Connection** → WebRTC establishes connection to FastAPI server
2. **User Input** → Audio/text sent via WebRTC data channel or REST API
3. **Processing** → Text converted to speech via TTS service
4. **Avatar Generation** → Selected AI model generates lip-synced video frames
5. **Response Streaming** → Animated avatar + audio streamed back via WebRTC

### Configuration System

**Command-line Arguments**
- `--avatar_id` - Avatar directory name in `data/avatars/`
- `--model` - AI model selection (wav2lip, musetalk, ultralight)
- `--listenport` - Server port (default: 8010)
- `--max_session` - Maximum concurrent sessions
- `--transport` - Transport method (webrtc, rtcpush, virtualcam)
- `--debug` - Enable debug logging

**Environment Variables** (`.env` file)
- Model paths, API keys, database URLs, service configurations
- See `docs/environment-setup.md` for full reference

## Code Quality Standards

### Required for All Code

**1. Google-Style Docstrings** - Mandatory for all functions and classes
```python
def process_audio(audio_chunk: bytes, sample_rate: int = 16000) -> str:
    """Process audio chunk and return transcript.

    Args:
        audio_chunk: Raw audio bytes in PCM format
        sample_rate: Audio sample rate in Hz

    Returns:
        Transcribed text from audio

    Raises:
        ValueError: If audio_chunk is empty or invalid format
        RuntimeError: If model inference fails
    """
    pass
```

**2. Type Hints** - Required for all function parameters and return values
```python
from typing import Dict, List, Optional, Tuple

def find_models(path: str, pattern: str = "*.pth") -> List[str]:
    """Find model files matching pattern."""
    pass
```

**3. Specific Exception Handling** - Never use bare `except Exception`
```python
# Good ✅
try:
    model.load_state_dict(checkpoint)
except FileNotFoundError as e:
    logger.error(f"Checkpoint not found: {e}")
    raise
except RuntimeError as e:
    logger.error(f"Failed to load model: {e}")
    raise

# Bad ❌
try:
    model.load_state_dict(checkpoint)
except Exception as e:
    logger.error(f"Error: {e}")
```

**4. Pylint Compliance**
- Must achieve Pylint score ≥ 7.0
- Critical errors (E, F) must be zero
- Run `pylint` before committing

### Git Workflow

**Branch Strategy**
```
main (production)
  └── develop (integration)
       ├── feature/your-feature-name
       ├── bugfix/issue-description
       └── hotfix/critical-fix
```

**Commit Message Format** (Conventional Commits)
```
<type>(<scope>): <subject>

<body>

<footer>
```

Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

Examples:
```
feat(tts): add ZipVoice Vietnamese TTS support

- Implemented ZipVoice service integration
- Added voice selection configuration
- Updated TTS service factory

Closes #123
```

```
fix(webrtc): resolve session cleanup memory leak

Fixed memory leak by properly closing media tracks
and cleaning up session state on disconnect.

Fixes #456
```

## Important File Locations

### Model Checkpoints
```
checkpoints/
├── synctalk/           # SyncTalk lip-sync model
├── whisper/            # Whisper ASR model cache
├── zipvoice/           # ZipVoice TTS model
├── qwen3/              # Qwen3 LLM model
├── face-parse-bisent/  # Face parsing model
└── wav2lip/            # Wav2Lip model weights
```

### Avatar Data
```
data/avatars/
└── avator_1/
    ├── full_imgs/      # Avatar image frames
    ├── config.yaml     # Avatar configuration
    └── audio/          # Audio samples
```

### Configuration Files
```
.pylintrc              # Pylint configuration
.pre-commit-config.yaml # Pre-commit hooks
.env                   # Environment variables (create from .env.example)
requirements.txt       # Production dependencies
requirements-dev.txt   # Development dependencies
```

## Development Workflow

### Adding a New AI Model

1. Create module directory: `src/modules/your_model/`
2. Implement model class inheriting from `BaseReal`:
```python
from src.core.base_real import BaseReal

class YourModel(BaseReal):
    def __init__(self, opt, model_path):
        super().__init__()
        # Initialize model

    def prepare_material(self, avatar_id):
        """Prepare avatar materials."""
        pass

    def process_frame(self, audio_chunk):
        """Process audio and generate video frame."""
        pass
```
3. Register in `src/services/real.py` `build_real()` function
4. Add configuration options and CLI arguments
5. Write tests in `tests/`
6. Update documentation

### Adding a New TTS Service

1. Implement service in `src/services/tts.py`
2. Follow existing TTS service pattern (EdgeTTS, FishTTS)
3. Add configuration in `.env` and command-line arguments
4. Update service factory/selection logic
5. Test with different voices and languages
6. Document in `docs/api-reference.md`

## Testing Strategy

### Unit Tests
- Place in `tests/unit/`
- Test individual functions and classes
- Mock external dependencies

### Integration Tests
- Place in `tests/integration/`
- Test component interactions
- Test full request/response flows

### Performance Tests
- Place in `tests/performance/`
- Measure latency and throughput
- Profile GPU memory usage

## Common Pitfalls to Avoid

1. **Never commit without running Pylint** - CI will fail if score < 7.0
2. **Always use type hints** - Required for MyPy type checking
3. **Don't use generic Exception catches** - Use specific exception types
4. **Check CUDA availability before GPU operations**:
```python
import torch
if torch.cuda.is_available():
    device = torch.device("cuda")
else:
    device = torch.device("cpu")
    logger.warning("CUDA not available, using CPU")
```
5. **Clean up resources properly** - Close files, release GPU memory, cleanup sessions
6. **Use logger instead of print** - All output should go through the logging system

## Project Status

**Completed:**
- FastAPI backend with WebRTC streaming
- Multiple AI model integrations (Wav2Lip, MuseTalk, Ultralight)
- TTS service layer (EdgeTTS, FishTTS, XTTS, etc.)
- Session management and multi-user support
- Web interface (dashboard, WebRTC API)
- Code quality standards (Pylint, pre-commit hooks)

**In Development (4-Week Sprint):**
- SyncTalk lip-sync integration
- Whisper ASR for Vietnamese
- ZipVoice TTS for Vietnamese
- LangGraph agent system (orchestrator, dialogue, reservation)
- RAG system with Qdrant vector database
- vLLM + Qwen3-8B local LLM

## Key Dependencies

```
PyTorch 2.7.1+          # ML framework
transformers 4.55.0+    # Hugging Face models
FastAPI 0.109+          # Web framework
aiortc 1.13.0+          # WebRTC implementation
edge-tts 7.2.0+         # TTS service
pylint 3.0.3+           # Code quality
```

## Resources

- Main README: `README.md`
- Development Guide: `docs/development.md` (4-week sprint plan, team structure)
- Architecture Details: `docs/architecture.md` (system design, data flow)
- Environment Setup: `docs/environment-setup.md` (installation, models, databases)
- API Reference: `docs/api-reference.md` (REST, WebSocket, WebRTC APIs)
- Git Workflow: `docs/branch-rule.md` (branching, commits, PRs)
- Contributing: `CONTRIBUTING.md` (code standards, testing, PR process)

## Quick Reference

**Start Development:**
```bash
source venv/bin/activate
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
python app.py --avatar_id avator_1 --debug
```

**Before Committing:**
```bash
pylint $(git ls-files '*.py') --fail-under=7.0
pre-commit run --all-files
pytest tests/
```

**Access Interfaces:**
- Dashboard: http://localhost:8010/dashboard.html
- WebRTC API: http://localhost:8010/webrtcapi.html
- API Docs: http://localhost:8010/docs
