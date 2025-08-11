#!/bin/bash

# Digital Human - Ultralight Model Runner
# Fast real-time inference with Ultralight model

set -e  # Exit on any error

echo "⚡ Starting Digital Human with Ultralight model..."

# Check if we're in the correct directory
if [ ! -f "app.py" ]; then
    echo "❌ Error: Please run this script from the Digital-Human root directory"
    echo "   cd Digital-Human && scripts/run_ultralight.sh"
    exit 1
fi

# Default configuration
MODEL="ultralight"
AVATAR="avator_1"
PORT="8010"
TTS="edgetts"
VOICE="en-US-AriaNeural"
BATCH_SIZE="8"  # Smaller batch size for faster inference

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --avatar)
            AVATAR="$2"
            shift 2
            ;;
        --port)
            PORT="$2"
            shift 2
            ;;
        --tts)
            TTS="$2"
            shift 2
            ;;
        --voice)
            VOICE="$2"
            shift 2
            ;;
        --batch-size)
            BATCH_SIZE="$2"
            shift 2
            ;;
        --help)
            echo "Usage: $0 [options]"
            echo "Options:"
            echo "  --avatar AVATAR_ID     Avatar to use (default: avator_1)"
            echo "  --port PORT           Server port (default: 8010)"
            echo "  --tts TTS_SERVICE     TTS service (default: edgetts)"
            echo "  --voice VOICE_ID      Voice ID (default: en-US-AriaNeural)"
            echo "  --batch-size SIZE     Batch size (default: 8)"
            echo "  --help               Show this help message"
            echo ""
            echo "Example:"
            echo "  $0 --avatar avator_1 --port 8011 --voice en-GB-SoniaNeural"
            echo ""
            echo "Note: Ultralight model is optimized for speed and requires:"
            echo "  - models/ultralight/ultralight.pth"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

echo "📋 Configuration:"
echo "   Model: $MODEL (Fast inference optimized)"
echo "   Avatar: $AVATAR"
echo "   Port: $PORT"
echo "   TTS: $TTS"
echo "   Voice: $VOICE"
echo "   Batch Size: $BATCH_SIZE"
echo ""

# Check if avatar exists
if [ ! -d "data/avatars/$AVATAR" ]; then
    echo "⚠️  Warning: Avatar directory 'data/avatars/$AVATAR' not found"
    echo "   Make sure your avatar files are in the correct location"
fi

# Check if model files exist
if [ ! -f "models/ultralight/ultralight.pth" ]; then
    echo "⚠️  Warning: Ultralight model file not found at 'models/ultralight/ultralight.pth'"
    echo "   Please ensure the model file is downloaded and placed correctly"
fi

echo "🚀 Starting server..."
echo "   Dashboard: http://localhost:$PORT/dashboard.html"
echo "   WebRTC API: http://localhost:$PORT/webrtcapi.html"
echo ""
echo "💡 Ultralight model is optimized for real-time performance"
echo "   Lower quality but faster inference suitable for live interaction"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Start the application
python app.py \
    --model "$MODEL" \
    --avatar_id "$AVATAR" \
    --listenport "$PORT" \
    --tts "$TTS" \
    --REF_FILE "$VOICE" \
    --batch_size "$BATCH_SIZE"