#!/bin/bash

# Digital Human - MuseTalk Model Runner
# High-quality facial animation with MuseTalk model

set -e  # Exit on any error

echo "🎨 Starting Digital Human with MuseTalk model..."

# Check if we're in the correct directory
if [ ! -f "app.py" ]; then
    echo "❌ Error: Please run this script from the Digital-Human root directory"
    echo "   cd Digital-Human && scripts/run_musetalk.sh"
    exit 1
fi

# Default configuration
MODEL="musetalk"
AVATAR="avator_1"
PORT="8010"
TTS="edgetts"
VOICE="en-US-AriaNeural"
BATCH_SIZE="16"

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
            echo "  --batch-size SIZE     Batch size (default: 16)"
            echo "  --help               Show this help message"
            echo ""
            echo "Example:"
            echo "  $0 --avatar avator_1 --port 8011 --voice en-GB-SoniaNeural"
            echo ""
            echo "Note: MuseTalk requires additional model files:"
            echo "  - models/musetalkV15/unet.pth"
            echo "  - models/musetalkV15/musetalk.json"
            echo "  - data/avatars/\$AVATAR/latents.pt"
            echo "  - data/avatars/\$AVATAR/mask/"
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
echo "   Model: $MODEL"
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

# Check MuseTalk-specific requirements
echo "🔍 Checking MuseTalk requirements..."
MISSING_FILES=()

if [ ! -d "models/musetalkV15" ]; then
    MISSING_FILES+=("models/musetalkV15/ directory")
fi

if [ ! -f "models/musetalkV15/unet.pth" ]; then
    MISSING_FILES+=("models/musetalkV15/unet.pth")
fi

if [ ! -f "models/musetalkV15/musetalk.json" ]; then
    MISSING_FILES+=("models/musetalkV15/musetalk.json")
fi

if [ ! -f "data/avatars/$AVATAR/latents.pt" ]; then
    MISSING_FILES+=("data/avatars/$AVATAR/latents.pt")
fi

if [ ! -d "data/avatars/$AVATAR/mask" ]; then
    MISSING_FILES+=("data/avatars/$AVATAR/mask/ directory")
fi

if [ ${#MISSING_FILES[@]} -gt 0 ]; then
    echo "❌ Missing required MuseTalk files:"
    for file in "${MISSING_FILES[@]}"; do
        echo "   - $file"
    done
    echo ""
    echo "Please ensure all MuseTalk model files and avatar-specific files are present."
    echo "You may need to generate avatar-specific files using the MuseTalk preparation tools."
    exit 1
fi

echo "✅ All MuseTalk requirements found"
echo ""

echo "🚀 Starting server..."
echo "   Dashboard: http://localhost:$PORT/dashboard.html"
echo "   WebRTC API: http://localhost:$PORT/webrtcapi.html"
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