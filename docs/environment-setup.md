# Environment Setup

Complete guide for setting up the Digital Human Restaurant Assistant development environment.

> **Modern Stack**: This project uses **UV** for fast package management and **pysen** for code formatting and linting.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Hardware Requirements](#hardware-requirements)
3. [Software Installation](#software-installation)
4. [Development Tools Setup](#development-tools-setup)
5. [Model Downloads](#model-downloads)
6. [Database Setup](#database-setup)
7. [Environment Variables](#environment-variables)
8. [Verification](#verification)
9. [Quick Start Test](#quick-start-test)
10. [Troubleshooting](#troubleshooting)

## Prerequisites

### Operating System

- **Linux**: Ubuntu 20.04+ (Recommended)
- **macOS**: 12+ (Intel or Apple Silicon)
- **Windows**: Windows 10/11 with WSL2 (Ubuntu 22.04)

### Required Software

| Software | Version | Purpose |
|----------|---------|---------|
| Python | 3.10+ | Runtime environment |
| UV | Latest | Fast package manager (recommended) |
| Git | 2.30+ | Version control |
| Docker | 24.0+ | Container deployment |
| CUDA | 11.8+ or 12.1+ | GPU acceleration |
| Node.js | 18+ (optional) | Frontend development |

## Hardware Requirements

### Minimum Requirements

```yaml
CPU: 8+ cores
RAM: 16GB
GPU: NVIDIA RTX 3060 12GB
Storage: 100GB SSD
Network: 10 Mbps+
```

### Recommended Requirements (Restaurant Production)

```yaml
CPU: 16+ cores (AMD Ryzen 9 / Intel i9)
RAM: 32GB DDR4/DDR5
GPU: NVIDIA RTX 4080 16GB or RTX 4090 24GB
Storage: 500GB NVMe SSD
Network: 100 Mbps+ (dedicated line)
```

### GPU Compatibility

Supported GPUs for real-time inference (<2s response time):

- ✅ **RTX 4090** (24GB) - Best performance
- ✅ **RTX 4080** (16GB) - Excellent
- ✅ **RTX 4060** (16GB) - Good
- ✅ **RTX 3090** (24GB) - Good
- ⚠️ **RTX 3060** (12GB) - Minimum, may need optimization
- ❌ **RTX 2060** (8GB) - Not recommended

## Software Installation

### 1. Python 3.10+ Setup

#### Ubuntu/Debian

```bash
# Add deadsnakes PPA
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt update

# Install Python 3.10
sudo apt install python3.10 python3.10-venv python3.10-dev

# Set as default (optional)
sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.10 1
```

#### macOS

```bash
# Using Homebrew
brew install python@3.10

# Verify installation
python3.10 --version
```

#### Windows (WSL2)

```bash
# Install WSL2 Ubuntu 22.04
wsl --install -d Ubuntu-22.04

# Inside WSL, follow Ubuntu instructions
sudo apt update
sudo apt install python3.10 python3.10-venv python3.10-dev
```

### 2. CUDA Installation

#### NVIDIA Driver

```bash
# Check current driver
nvidia-smi

# Install latest driver (if needed)
sudo ubuntu-drivers autoinstall
# or
sudo apt install nvidia-driver-535
```

#### CUDA Toolkit 12.1

```bash
# Download and install
wget https://developer.download.nvidia.com/compute/cuda/12.1.0/local_installers/cuda_12.1.0_530.30.02_linux.run
sudo sh cuda_12.1.0_530.30.02_linux.run

# Add to PATH
echo 'export PATH=/usr/local/cuda-12.1/bin:$PATH' >> ~/.bashrc
echo 'export LD_LIBRARY_PATH=/usr/local/cuda-12.1/lib64:$LD_LIBRARY_PATH' >> ~/.bashrc
source ~/.bashrc

# Verify
nvcc --version
```

### 3. Docker & NVIDIA Container Runtime

```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Add user to docker group
sudo usermod -aG docker $USER
newgrp docker

# Install NVIDIA Container Toolkit
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | \
  sudo tee /etc/apt/sources.list.d/nvidia-docker.list

sudo apt-get update
sudo apt-get install -y nvidia-docker2
sudo systemctl restart docker

# Test GPU in Docker
docker run --rm --gpus all nvidia/cuda:12.1.0-base-ubuntu22.04 nvidia-smi
```

### 4. Git & Git LFS

```bash
# Install Git
sudo apt install git

# Install Git LFS (for large model files)
curl -s https://packagecloud.io/install/repositories/github/git-lfs/script.deb.sh | sudo bash
sudo apt-get install git-lfs
git lfs install

# Configure Git
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

### 5. UV Package Manager (Recommended)

UV is a fast Python package manager written in Rust, replacing pip for better performance.

```bash
# Install UV
curl -LsSf https://astral.sh/uv/install.sh | sh

# Or using pip
pip install uv

# Verify installation
uv --version

# Add to PATH (if needed)
echo 'export PATH="$HOME/.cargo/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

## Development Tools Setup

### 1. Clone Repository

```bash
# Clone with submodules
git clone --recursive https://github.com/hungho77/Digital-Human.git
cd Digital-Human

# If already cloned, init submodules
git submodule update --init --recursive
```

### 2. Virtual Environment with UV

**Option A: Using UV (Recommended - Fast & Modern)**

```bash
# Create virtual environment with UV
uv venv

# Activate
source .venv/bin/activate  # Linux/Mac
# or
.venv\Scripts\activate  # Windows

# Install dependencies with UV (uses uv.lock for reproducible builds)
uv pip install -r requirements.txt

# Install development dependencies
uv pip install -r requirements-dev.txt

# UV will automatically use uv.lock if available for exact versions
```

**Option B: Traditional pip (Alternative)**

```bash
# Create virtual environment
python3.10 -m venv venv

# Activate
source venv/bin/activate  # Linux/Mac

# Upgrade pip
pip install --upgrade pip setuptools wheel

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### 3. Install Development Tools

```bash
# Install pre-commit hooks
pre-commit install

# Install code formatting and quality tools
uv pip install pysen[lint] black flake8 isort

# Or with traditional pip
pip install pysen[lint] black flake8 isort

# Verify installations
uv pip list | grep -E "torch|transformers|fastapi|pysen|black|flake8"
```

### 4. Code Quality Tools

```bash
# Install via requirements-dev.txt (includes):
# - pylint (code quality)
# - mypy (type checking)
# - bandit (security)
# - pytest (testing)
# - pysen (formatting and linting orchestrator)
# - black (code formatter)
# - flake8 (linting)
# - isort (import sorting)

# Verify tools installation
pylint --version
mypy --version
pytest --version
pysen --version
black --version
flake8 --version
isort --version

# List pysen available targets
pysen list

# Run pysen format (auto-fix: isort + black)
pysen run format

# Run pysen lint (check: isort + black + flake8 + mypy)
pysen run lint

# Lint specific files
pysen run_files lint src/services/real.py
```

### 5. Lock Dependencies (Reproducible Builds)

```bash
# Generate uv.lock file for exact dependency versions
uv pip compile requirements.txt -o uv.lock

# Install from lock file (ensures exact versions)
uv pip sync uv.lock

# Update dependencies
uv pip compile --upgrade requirements.txt -o uv.lock
```

## Model Downloads

### AI Models Required

```bash
# Create checkpoints directory (updated structure)
mkdir -p checkpoints/{synctalk,whisper,zipvoice,qwen3}
mkdir -p data/avatars/avator_1
```

### 1. vLLM Model (LLM for Agents)

```bash
# Download Qwen3-8B-Instruct (Vietnamese support)
# Using UV for faster installation
uv pip install huggingface-hub

python -c "
from huggingface_hub import snapshot_download
snapshot_download(
    repo_id='Qwen/Qwen3-8B-Instruct',
    local_dir='./checkpoints/qwen3',
    cache_dir='./cache'
)
"

# Or using git clone for large models
git lfs install
git clone https://huggingface.co/Qwen/Qwen3-8B-Instruct checkpoints/qwen3
```

### 2. Whisper Model (Speech-to-Text)

```bash
# Download faster-whisper models
uv pip install faster-whisper

python -c "
from faster_whisper import WhisperModel
# Downloads to cache automatically
model = WhisperModel('large-v3', device='cuda', compute_type='float16')
print('Whisper model downloaded successfully')
"

# Models will be cached in checkpoints/whisper/
```

### 3. ZipVoice TTS Model (Vietnamese)

```bash
# Download ZipVoice model for Vietnamese TTS
# Follow ZipVoice installation guide
uv pip install zipvoice

# Download Vietnamese voice model
python -c "
from zipvoice import download_model
download_model('vietnamese', save_dir='./checkpoints/zipvoice')
"
```

### 4. SyncTalk Lip-sync Model

```bash
# Download SyncTalk model for high-quality lip-sync
cd checkpoints/synctalk

# Download from official repository
wget https://huggingface.co/vinthony/SyncTalk/resolve/main/synctalk_model.pth

# Or use git LFS
git lfs install
git clone https://huggingface.co/vinthony/SyncTalk .
```

### 5. Sentence Transformers (RAG)

```bash
# Download embedding models for Vietnamese
uv pip install sentence-transformers

python -c "
from sentence_transformers import SentenceTransformer
# Use multilingual model for Vietnamese support
model = SentenceTransformer('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')
model.save('./checkpoints/embeddings/multilingual-MiniLM')
print('Embedding model downloaded successfully')
"
```

### 6. Alternative: Automated Model Download

```bash
# Use the automated download script
./scripts/download_models.sh

# This will download all required models:
# - Qwen3-8B-Instruct (LLM)
# - Whisper Large V3 (ASR)
# - ZipVoice Vietnamese (TTS)
# - SyncTalk (Lip-sync)
# - Multilingual embeddings (RAG)
```

## Environment Variables

### Create `.env` File

```bash
# Copy template
cp .env.example .env

# Edit configuration
nano .env
```

### Environment Configuration

```bash
# .env file content
# ===================

# Application Settings
APP_NAME=Digital-Human-Restaurant
ENVIRONMENT=development  # development | production
DEBUG=true
LOG_LEVEL=INFO

# Server Configuration
HOST=0.0.0.0
PORT=8010
MAX_SESSIONS=5
WORKERS=4

# Model Paths (Updated Structure)
CHECKPOINT_PATH=./checkpoints
AVATAR_PATH=./data/avatars
CACHE_PATH=./cache

# AI Model Selection
DEFAULT_AVATAR=avator_1

# Lip-sync Configuration
LIPSYNC_MODEL=synctalk
SYNCTALK_CHECKPOINT=./checkpoints/synctalk/synctalk_model.pth

# vLLM Configuration (Vietnamese LLM)
LLM_PROVIDER=local  # local | openai | anthropic | google
LLM_MODEL=./checkpoints/qwen3
VLLM_GPU_MEMORY=0.8
VLLM_MAX_TOKENS=2048
VLLM_TEMPERATURE=0.7

# Whisper Configuration (ASR)
WHISPER_MODEL=large-v3
WHISPER_CHECKPOINT=./checkpoints/whisper
WHISPER_LANGUAGE=vi  # Vietnamese
WHISPER_DEVICE=cuda
WHISPER_COMPUTE_TYPE=float16

# TTS Configuration (ZipVoice)
TTS_SERVICE=zipvoice  # zipvoice | edgetts | fishtts | xtts
TTS_CHECKPOINT=./checkpoints/zipvoice
TTS_VOICE=vietnamese_female
TTS_SPEED=1.0
TTS_SERVER=http://localhost:9880  # If using server mode

# Database Configuration
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=digital_human
POSTGRES_USER=digitaluser
POSTGRES_PASSWORD=your_secure_password

# Redis Configuration
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=your_redis_password

# Vector Database (Qdrant) for RAG
QDRANT_HOST=localhost
QDRANT_PORT=6333
QDRANT_COLLECTION=restaurant_knowledge
EMBEDDING_MODEL=./checkpoints/embeddings/multilingual-MiniLM
EMBEDDING_DIMENSION=384

# WebRTC Configuration
STUN_SERVER=stun:stun.l.google.com:19302
TURN_SERVER=turn:your-turn-server.com:3478
TURN_USERNAME=username
TURN_PASSWORD=password

# Security
SECRET_KEY=your-secret-key-change-in-production
API_KEY=your-api-key
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8010

# Restaurant Configuration
RESTAURANT_NAME=Your Restaurant Name
RESTAURANT_TIMEZONE=Asia/Ho_Chi_Minh
RESTAURANT_LANGUAGE=vi
```

### Export Environment Variables

```bash
# Load .env file
export $(cat .env | grep -v '^#' | xargs)

# Or use direnv (recommended)
sudo apt install direnv
echo 'eval "$(direnv hook bash)"' >> ~/.bashrc
source ~/.bashrc
direnv allow .
```

## Database Setup

### PostgreSQL

```bash
# Install PostgreSQL
sudo apt install postgresql postgresql-contrib

# Create database and user
sudo -u postgres psql <<EOF
CREATE DATABASE digital_human;
CREATE USER digitaluser WITH ENCRYPTED PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE digital_human TO digitaluser;
\q
EOF

# Test connection
psql -h localhost -U digitaluser -d digital_human
```

### Redis

```bash
# Install Redis
sudo apt install redis-server

# Configure Redis
sudo nano /etc/redis/redis.conf
# Set: requirepass your_redis_password

# Restart Redis
sudo systemctl restart redis-server

# Test connection
redis-cli
AUTH your_redis_password
PING
```

### Qdrant (Vector Database)

```bash
# Install via Docker (recommended)
docker run -d \
  --name qdrant \
  -p 6333:6333 \
  -v $(pwd)/data/qdrant:/qdrant/storage \
  qdrant/qdrant

# Or install locally
curl -L https://github.com/qdrant/qdrant/releases/latest/download/qdrant-x86_64-unknown-linux-gnu.tar.gz | tar xz
./qdrant
```

## Verification

### System Check Script

```bash
# Run verification
./scripts/verify_setup.sh

# Or manual checks with UV
python -c "import torch; print(f'PyTorch: {torch.__version__}')"
python -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}')"
python -c "import transformers; print(f'Transformers: {transformers.__version__}')"
```

### UV and Package Verification

```bash
# Verify UV installation
uv --version

# Check installed packages
uv pip list | grep -E "torch|transformers|fastapi|pysen"

# Verify uv.lock exists
ls -lh uv.lock

# Check pysen configuration
pysen --version
pysen run lint --check

# Verify all dependencies from lock file
uv pip check
```

### GPU Verification

```bash
# Check NVIDIA GPU
nvidia-smi

# Check CUDA in Python
python -c "
import torch
print(f'CUDA Available: {torch.cuda.is_available()}')
print(f'CUDA Version: {torch.version.cuda}')
print(f'GPU Count: {torch.cuda.device_count()}')
if torch.cuda.is_available():
    print(f'GPU Name: {torch.cuda.get_device_name(0)}')
    print(f'GPU Memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.2f} GB')
"
```

### Service Health Checks

```bash
# Check PostgreSQL
pg_isready -h localhost -p 5432

# Check Redis
redis-cli ping

# Check Qdrant
curl http://localhost:6333/healthz

# Check all services
make health-check
```

## Quick Start Test

```bash
# Activate environment (if using UV)
source .venv/bin/activate

# Or traditional venv
source venv/bin/activate

# Run quick test
python -c "
import torch
from src.services.real import RealService

print('✅ PyTorch:', torch.__version__)
print('✅ CUDA Available:', torch.cuda.is_available())
print('✅ Configuration loaded successfully')
"

# Format code with pysen
pysen run format

# Lint code with pysen
pysen run lint

# Run development server
python app.py --avatar_id avator_1 --debug

# Access dashboard
# http://localhost:8010/dashboard.html
```

## Troubleshooting

### Common Issues

#### 1. CUDA Not Found

```bash
# Check CUDA installation
ls /usr/local/cuda*/

# Set CUDA path manually
export CUDA_HOME=/usr/local/cuda-12.1
export PATH=$CUDA_HOME/bin:$PATH
export LD_LIBRARY_PATH=$CUDA_HOME/lib64:$LD_LIBRARY_PATH
```

#### 2. Out of Memory

```bash
# Reduce model memory usage
export PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:512

# Use smaller batch size
python app.py --batch_size 4
```

#### 3. Port Already in Use

```bash
# Check what's using port 8010
lsof -i :8010
sudo netstat -tulpn | grep 8010

# Kill process
kill -9 <PID>

# Or use different port
python app.py --listenport 8011
```

#### 4. Model Download Fails

```bash
# Use mirrors for China/Asia
export HF_ENDPOINT=https://hf-mirror.com
uv pip install huggingface-hub

# Or download manually from browser
```

#### 5. UV Installation Issues

```bash
# If curl install fails, use pip
pip install uv

# Or install from source
cargo install --git https://github.com/astral-sh/uv

# Verify installation
which uv
uv --version
```

#### 6. Pysen Configuration Issues

```bash
# Verify pyproject.toml exists and has [tool.pysen] section
cat pyproject.toml | grep -A 20 "\[tool.pysen\]"

# List available pysen targets
pysen list

# Run pysen with verbose output
pysen --loglevel debug run lint

# Install missing dependencies
uv pip install black flake8 isort
```

## Next Steps

1. ✅ Environment setup complete
2. 📖 Read [development.md](./development.md) for development workflow
3. 🏗️ Review [architecture.md](./architecture.md) for system design
4. 🚀 Check [deployment.md](./deployment.md) for production deployment
5. 📚 Explore [api-reference.md](./api-reference.md) for API documentation

## Additional Resources

### Core Technologies
- [Python Official Documentation](https://docs.python.org/3.10/)
- [PyTorch Installation Guide](https://pytorch.org/get-started/locally/)
- [NVIDIA CUDA Installation](https://developer.nvidia.com/cuda-downloads)
- [Docker Documentation](https://docs.docker.com/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)

### Package Management & Code Quality
- [UV - Fast Python Package Manager](https://github.com/astral-sh/uv)
- [Pysen - Python Code Formatter & Linter](https://github.com/pfnet/pysen)
- [Black Code Formatter](https://black.readthedocs.io/)
- [isort Import Sorter](https://pycqa.github.io/isort/)
- [Pylint](https://pylint.pycqa.org/)
- [MyPy Type Checker](https://mypy.readthedocs.io/)

### AI Models
- [Qwen3 Model](https://huggingface.co/Qwen/Qwen3-8B-Instruct)
- [Whisper ASR](https://github.com/openai/whisper)
- [SyncTalk Lip-sync](https://github.com/ZiqiaoPeng/SyncTalk)
- [Sentence Transformers](https://www.sbert.net/)

### Databases & Vector Search
- [PostgreSQL](https://www.postgresql.org/docs/)
- [Redis](https://redis.io/docs/)
- [Qdrant Vector Database](https://qdrant.tech/documentation/)

## Support

For setup issues:
1. Check [troubleshooting section](#troubleshooting)
2. Review GitHub Issues
3. Contact: [your-support-email]
4. Community: [discord/slack link]

