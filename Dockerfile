# Digital Human - Modern Docker Configuration
# Supports latest PyTorch, WebRTC, and all AI models

ARG CUDA_VERSION=12.1.0
ARG UBUNTU_VERSION=22.04
FROM nvidia/cuda:${CUDA_VERSION}-cudnn8-devel-ubuntu${UBUNTU_VERSION}

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV DEBIAN_FRONTEND=noninteractive

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-dev \
    pkg-config \
    wget \
    curl \
    git \
    vim \
    ffmpeg \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libfontconfig1 \
    libxrender1 \
    libgl1-mesa-glx \
    libasound2-dev \
    portaudio19-dev \
    && rm -rf /var/lib/apt/lists/*

# Create symbolic link for python
RUN ln -s /usr/bin/python3 /usr/bin/python

# Upgrade pip
RUN pip install --upgrade pip setuptools wheel

# Copy requirements first for better Docker layer caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install additional dependencies for Docker environment
RUN pip install --no-cache-dir \
    gunicorn \
    uvicorn[standard]

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p data/avatars data/models logs

# Set permissions for scripts
RUN chmod +x scripts/*.sh

# Create non-root user for security
RUN groupadd -r digitaluser && useradd -r -g digitaluser digitaluser
RUN chown -R digitaluser:digitaluser /app
USER digitaluser

# Expose port
EXPOSE 8010

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8010/ || exit 1

# Default command - use quick start script
CMD ["./scripts/quick_start.sh"]