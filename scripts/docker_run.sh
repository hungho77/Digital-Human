#!/bin/bash

# Digital Human - Docker Management Script
# Build and run Digital Human in Docker container

set -e

echo "🐳 Digital Human Docker Management"

# Default configuration
ACTION="run"
MODEL="wav2lip"
PORT="8010"
GPU_ENABLED=true
DETACHED=false
BUILD=false

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        build)
            ACTION="build"
            shift
            ;;
        run)
            ACTION="run"
            shift
            ;;
        stop)
            ACTION="stop"
            shift
            ;;
        logs)
            ACTION="logs"
            shift
            ;;
        --model)
            MODEL="$2"
            shift 2
            ;;
        --port)
            PORT="$2"
            shift 2
            ;;
        --no-gpu)
            GPU_ENABLED=false
            shift
            ;;
        --detach|-d)
            DETACHED=true
            shift
            ;;
        --build)
            BUILD=true
            shift
            ;;
        --help)
            echo "Usage: $0 [action] [options]"
            echo ""
            echo "Actions:"
            echo "  build              Build Docker image"
            echo "  run                Run container (default)"
            echo "  stop               Stop running container"
            echo "  logs               Show container logs"
            echo ""
            echo "Options:"
            echo "  --model MODEL      AI model to use (wav2lip|musetalk|ultralight)"
            echo "  --port PORT        Host port to bind (default: 8010)"
            echo "  --no-gpu           Disable GPU support"
            echo "  --detach, -d       Run container in background"
            echo "  --build            Build image before running"
            echo "  --help             Show this help message"
            echo ""
            echo "Examples:"
            echo "  $0 build                          # Build Docker image"
            echo "  $0 run --model wav2lip            # Run with Wav2Lip model"
            echo "  $0 run --port 8011 --detach      # Run on port 8011 in background"
            echo "  $0 --build run --model musetalk  # Build and run with MuseTalk"
            echo "  $0 stop                           # Stop running container"
            echo "  $0 logs                           # View container logs"
            echo ""
            echo "Prerequisites:"
            echo "  - Docker installed and running"
            echo "  - NVIDIA Docker runtime (for GPU support)"
            echo "  - Model files in ./models/ directory"
            echo "  - Avatar files in ./data/avatars/ directory"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Docker image and container names
IMAGE_NAME="digital-human"
CONTAINER_NAME="digital-human-container"

case $ACTION in
    build)
        echo "🔨 Building Docker image..."
        
        if [ "$GPU_ENABLED" = true ]; then
            echo "   GPU support: Enabled"
            docker build -t $IMAGE_NAME \
                --build-arg CUDA_VERSION=12.1.0 \
                --build-arg UBUNTU_VERSION=22.04 \
                .
        else
            echo "   GPU support: Disabled"
            docker build -t $IMAGE_NAME \
                --build-arg BASE_IMAGE=ubuntu:22.04 \
                .
        fi
        
        echo "✅ Docker image built successfully: $IMAGE_NAME"
        ;;
        
    run)
        # Build if requested
        if [ "$BUILD" = true ]; then
            echo "🔨 Building Docker image first..."
            $0 build $([ "$GPU_ENABLED" = false ] && echo "--no-gpu")
            echo ""
        fi
        
        # Stop existing container if running
        if docker ps -q -f name=$CONTAINER_NAME | grep -q .; then
            echo "🛑 Stopping existing container..."
            docker stop $CONTAINER_NAME >/dev/null 2>&1
            docker rm $CONTAINER_NAME >/dev/null 2>&1
        fi
        
        echo "🚀 Starting Digital Human container..."
        echo "   Model: $MODEL"
        echo "   Port: $PORT"
        echo "   GPU: $([ "$GPU_ENABLED" = true ] && echo "Enabled" || echo "Disabled")"
        echo "   Mode: $([ "$DETACHED" = true ] && echo "Background" || echo "Interactive")"
        echo ""
        
        # Prepare Docker run command
        DOCKER_CMD="docker run"
        
        # Container options
        if [ "$DETACHED" = true ]; then
            DOCKER_CMD="$DOCKER_CMD -d"
        else
            DOCKER_CMD="$DOCKER_CMD -it"
        fi
        
        DOCKER_CMD="$DOCKER_CMD --name $CONTAINER_NAME"
        DOCKER_CMD="$DOCKER_CMD --rm"
        DOCKER_CMD="$DOCKER_CMD -p $PORT:8010"
        
        # GPU support
        if [ "$GPU_ENABLED" = true ]; then
            DOCKER_CMD="$DOCKER_CMD --gpus all"
        fi
        
        # Volume mounts
        DOCKER_CMD="$DOCKER_CMD -v $(pwd)/data:/app/data"
        DOCKER_CMD="$DOCKER_CMD -v $(pwd)/models:/app/models"
        DOCKER_CMD="$DOCKER_CMD -v $(pwd)/logs:/app/logs"
        
        # Environment variables
        if [ ! -z "$OPENAI_API_KEY" ]; then
            DOCKER_CMD="$DOCKER_CMD -e OPENAI_API_KEY=$OPENAI_API_KEY"
        fi
        
        # Image and command
        DOCKER_CMD="$DOCKER_CMD $IMAGE_NAME"
        DOCKER_CMD="$DOCKER_CMD ./scripts/run_${MODEL}.sh"
        
        # Execute
        echo "🌐 Container will be available at: http://localhost:$PORT/dashboard.html"
        echo ""
        
        if [ "$DETACHED" = true ]; then
            echo "Starting in background mode..."
            echo "Use '$0 logs' to view logs"
            echo "Use '$0 stop' to stop the container"
            echo ""
        fi
        
        eval $DOCKER_CMD
        ;;
        
    stop)
        echo "🛑 Stopping Digital Human container..."
        
        if docker ps -q -f name=$CONTAINER_NAME | grep -q .; then
            docker stop $CONTAINER_NAME
            echo "✅ Container stopped"
        else
            echo "ℹ️  No running container found"
        fi
        ;;
        
    logs)
        echo "📋 Digital Human container logs:"
        echo ""
        
        if docker ps -a -q -f name=$CONTAINER_NAME | grep -q .; then
            docker logs -f $CONTAINER_NAME
        else
            echo "❌ No container found"
            echo "Use '$0 run' to start the container first"
        fi
        ;;
        
    *)
        echo "❌ Unknown action: $ACTION"
        echo "Use --help for usage information"
        exit 1
        ;;
esac