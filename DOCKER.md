# Digital Human - Docker Deployment Guide

This guide covers how to build and run the Digital Human application using Docker containers.

## 🐳 Quick Start

### Prerequisites
- Docker installed and running
- NVIDIA Docker runtime (for GPU support)
- Model files downloaded (see [Model Setup](#model-setup))

### Simple Run
```bash
# Build and run with Wav2Lip model
./scripts/docker_run.sh --build run --model wav2lip

# Quick start (auto-detects best model)
docker-compose up
```

## 📋 Available Methods

### Method 1: Docker Run Script (Recommended)
```bash
# Interactive mode
./scripts/docker_run.sh run --model wav2lip

# Background mode
./scripts/docker_run.sh run --model musetalk --detach

# Custom port
./scripts/docker_run.sh run --model ultralight --port 8011
```

### Method 2: Docker Compose
```bash
# Start all services
docker-compose up

# Background mode
docker-compose up -d

# With custom model
MODEL=musetalk docker-compose up
```

### Method 3: Manual Docker Commands
```bash
# Build
docker build -t digital-human .

# Run
docker run -it --gpus all \
  -p 8010:8010 \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/models:/app/models \
  digital-human
```

## 🛠 Configuration Options

### Docker Run Script Options
```bash
./scripts/docker_run.sh [action] [options]

Actions:
  build              Build Docker image
  run                Run container (default)
  stop               Stop running container
  logs               Show container logs

Options:
  --model MODEL      AI model (wav2lip|musetalk|ultralight)
  --port PORT        Host port (default: 8010)
  --no-gpu           Disable GPU support
  --detach, -d       Run in background
  --build            Build before running
```

### Environment Variables
```bash
# Set in docker-compose.yml or pass to docker run
OPENAI_API_KEY=your-key-here          # For LLM features
CUDA_VISIBLE_DEVICES=0                # GPU selection
PYTHONPATH=/app                       # Python path
```

## 📁 Model Setup

### Required Model Files
Place your model files in the following structure:
```
models/
├── wav2lip/
│   └── wav2lip.pth
├── musetalkV15/
│   ├── unet.pth
│   └── musetalk.json
└── ultralight/
    └── ultralight.pth

data/
└── avatars/
    └── avator_1/
        ├── coords.pkl
        ├── full_imgs/
        ├── face_imgs/
        ├── latents.pt      # For MuseTalk
        └── mask/           # For MuseTalk
```

### Model Download
```bash
# Models are typically large (500MB - 2GB)
# Download from the official repositories:
# - Wav2Lip: Place in models/wav2lip/
# - MuseTalk: Place in models/musetalkV15/
# - Ultralight: Place in models/ultralight/
```

## 🔧 Development

### Building Custom Images
```bash
# Standard build
docker build -t digital-human .

# With custom CUDA version
docker build -t digital-human \
  --build-arg CUDA_VERSION=11.8.0 \
  --build-arg UBUNTU_VERSION=22.04 .

# CPU-only build
docker build -t digital-human-cpu \
  --build-arg BASE_IMAGE=ubuntu:22.04 .
```

### Volume Mounts for Development
```bash
docker run -it \
  -p 8010:8010 \
  -v $(pwd):/app \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/models:/app/models \
  --gpus all \
  digital-human bash
```

## 🌐 Production Deployment

### With Nginx Reverse Proxy
```bash
# Start with nginx proxy
docker-compose --profile production up -d

# Access via nginx
curl http://localhost/
```

### Docker Swarm
```yaml
# docker-stack.yml
version: '3.8'
services:
  digital-human:
    image: digital-human
    ports:
      - "8010:8010"
    deploy:
      replicas: 2
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
```

```bash
docker stack deploy -c docker-stack.yml digital-human-stack
```

### Kubernetes
```yaml
# k8s-deployment.yml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: digital-human
spec:
  replicas: 1
  selector:
    matchLabels:
      app: digital-human
  template:
    metadata:
      labels:
        app: digital-human
    spec:
      containers:
      - name: digital-human
        image: digital-human:latest
        ports:
        - containerPort: 8010
        resources:
          limits:
            nvidia.com/gpu: 1
```

## 🐛 Troubleshooting

### Common Issues

#### GPU Not Detected
```bash
# Check NVIDIA Docker runtime
docker run --rm --gpus all nvidia/cuda:12.1.0-base-ubuntu22.04 nvidia-smi

# If fails, install nvidia-container-runtime
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | \
  sudo tee /etc/apt/sources.list.d/nvidia-docker.list
sudo apt-get update && sudo apt-get install -y nvidia-docker2
sudo systemctl restart docker
```

#### Port Already in Use
```bash
# Use different port
./scripts/docker_run.sh run --port 8011

# Check what's using the port
netstat -tulpn | grep 8010
```

#### Model Files Not Found
```bash
# Check volume mounts
docker run --rm -v $(pwd)/models:/app/models digital-human ls -la /app/models

# Ensure files exist locally
ls -la models/wav2lip/
ls -la data/avatars/avator_1/
```

#### Memory Issues
```bash
# Limit container memory
docker run --memory=4g --gpus all digital-human

# Monitor usage
docker stats
```

### Debugging
```bash
# Run with bash for debugging
docker run -it --gpus all \
  -v $(pwd):/app \
  digital-human bash

# View logs
./scripts/docker_run.sh logs

# Check container status
docker ps -a
docker inspect digital-human-container
```

## 📊 Performance

### Resource Requirements
- **CPU**: 4+ cores recommended
- **RAM**: 8GB minimum, 16GB recommended
- **GPU**: NVIDIA GTX 1060+ or equivalent
- **Storage**: 10GB for models and data

### Optimization Tips
```dockerfile
# Use multi-stage builds to reduce image size
FROM nvidia/cuda:12.1.0-cudnn8-runtime-ubuntu22.04 as runtime
COPY --from=builder /app /app

# Use specific Python base images
FROM python:3.11-slim as base

# Cache pip packages
RUN pip install --no-cache-dir -r requirements.txt
```

## 🔒 Security

### Production Security
```bash
# Run as non-root user (already implemented)
USER digitaluser

# Use secrets for API keys
echo "your-api-key" | docker secret create openai_key -
```

### Network Security
```yaml
# docker-compose.yml
networks:
  digital-human:
    driver: bridge
    internal: true  # No external access
```

## 📈 Monitoring

### Health Checks
```bash
# Manual health check
curl -f http://localhost:8010/ || echo "Service down"

# View health status
docker ps --format "table {{.Names}}\t{{.Status}}"
```

### Logging
```bash
# Follow logs
docker logs -f digital-human-container

# Export logs
docker logs digital-human-container > digital-human.log 2>&1
```