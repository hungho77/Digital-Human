#!/bin/bash

# Digital Human - Run with Validation
# Comprehensive startup validation and model selection

set -e  # Exit on any error

echo "🔍 Digital Human - Startup with Validation"

# Check if we're in the correct directory
if [ ! -f "app.py" ]; then
    echo "❌ Error: Please run this script from the Digital-Human root directory"
    echo "   cd Digital-Human && scripts/run_with_validation.sh"
    exit 1
fi

# Default configuration
MODEL=""
AVATAR="avator_1"
PORT="8010"
TTS="edgetts"
VOICE="en-US-AriaNeural"
BATCH_SIZE="16"

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --model)
            MODEL="$2"
            shift 2
            ;;
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
            echo "  --model MODEL         AI model (musetalk|wav2lip|ultralight)"
            echo "  --avatar AVATAR_ID    Avatar to use (default: avator_1)"
            echo "  --port PORT          Server port (default: 8010)"
            echo "  --tts TTS_SERVICE    TTS service (default: edgetts)"
            echo "  --voice VOICE_ID     Voice ID (default: en-US-AriaNeural)"
            echo "  --batch-size SIZE    Batch size (default: 16)"
            echo "  --help              Show this help message"
            echo ""
            echo "Example:"
            echo "  $0 --model wav2lip --avatar avator_1"
            echo ""
            echo "If no model is specified, this script will:"
            echo "  1. Run dependency validation"
            echo "  2. Check available models and files"
            echo "  3. Recommend the best model to use"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

echo "🔧 Running comprehensive validation..."
echo ""

# Run the validation script
python run.py --check-only

echo ""
echo "📊 Analysis complete. Checking available models..."
echo ""

# Check which models are available
AVAILABLE_MODELS=()

# Check Wav2Lip
if [ -f "models/wav2lip/wav2lip.pth" ]; then
    AVAILABLE_MODELS+=("wav2lip")
    echo "✅ Wav2Lip model available"
else
    echo "❌ Wav2Lip model missing (models/wav2lip/wav2lip.pth)"
fi

# Check MuseTalk
if [ -f "models/musetalkV15/unet.pth" ] && [ -f "data/avatars/$AVATAR/latents.pt" ]; then
    AVAILABLE_MODELS+=("musetalk")
    echo "✅ MuseTalk model available"
else
    echo "❌ MuseTalk model missing (requires models/musetalkV15/ and avatar-specific files)"
fi

# Check Ultralight
if [ -f "models/ultralight/ultralight.pth" ]; then
    AVAILABLE_MODELS+=("ultralight")
    echo "✅ Ultralight model available"
else
    echo "❌ Ultralight model missing (models/ultralight/ultralight.pth)"
fi

echo ""

if [ ${#AVAILABLE_MODELS[@]} -eq 0 ]; then
    echo "❌ No models are available. Please download at least one model:"
    echo "   - Wav2Lip: Place wav2lip.pth in models/wav2lip/"
    echo "   - MuseTalk: Place unet.pth in models/musetalkV15/"
    echo "   - Ultralight: Place ultralight.pth in models/ultralight/"
    exit 1
fi

# Model selection logic
if [ -z "$MODEL" ]; then
    echo "🤖 Model auto-selection:"
    if [[ " ${AVAILABLE_MODELS[@]} " =~ " wav2lip " ]]; then
        MODEL="wav2lip"
        echo "   Selected: Wav2Lip (recommended - best balance of quality and compatibility)"
    elif [[ " ${AVAILABLE_MODELS[@]} " =~ " ultralight " ]]; then
        MODEL="ultralight"
        echo "   Selected: Ultralight (fast inference)"
    elif [[ " ${AVAILABLE_MODELS[@]} " =~ " musetalk " ]]; then
        MODEL="musetalk"
        echo "   Selected: MuseTalk (high quality)"
    fi
else
    if [[ ! " ${AVAILABLE_MODELS[@]} " =~ " $MODEL " ]]; then
        echo "❌ Requested model '$MODEL' is not available"
        echo "Available models: ${AVAILABLE_MODELS[*]}"
        exit 1
    fi
    echo "✅ Using requested model: $MODEL"
fi

echo ""
echo "📋 Final Configuration:"
echo "   Model: $MODEL"
echo "   Avatar: $AVATAR"
echo "   Port: $PORT"
echo "   TTS: $TTS"
echo "   Voice: $VOICE"
echo "   Batch Size: $BATCH_SIZE"
echo ""

echo "🚀 Starting server with validation complete..."
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