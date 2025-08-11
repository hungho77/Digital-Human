#!/bin/bash

# Digital Human - Quick Start Script
# Fast startup with minimal configuration

set -e  # Exit on any error

echo "🚀 Digital Human - Quick Start"

# Check if we're in the correct directory
if [ ! -f "app.py" ]; then
    echo "❌ Error: Please run this script from the Digital-Human root directory"
    echo "   cd Digital-Human && scripts/quick_start.sh"
    exit 1
fi

echo "⚡ Starting with default configuration..."
echo "   Model: wav2lip (best compatibility)"
echo "   Avatar: avator_1" 
echo "   Port: 8010"
echo "   TTS: EdgeTTS (en-US-AriaNeural)"
echo ""

# Quick model check
if [ ! -f "models/wav2lip/wav2lip.pth" ]; then
    echo "⚠️  Warning: Wav2Lip model not found, attempting to find alternative..."
    
    if [ -f "models/ultralight/ultralight.pth" ]; then
        echo "✅ Using Ultralight model instead"
        MODEL="ultralight"
    elif [ -f "models/musetalkV15/unet.pth" ]; then
        echo "✅ Using MuseTalk model instead"
        MODEL="musetalk"
    else
        echo "❌ No models found! Please download at least one model file."
        echo "   Run: scripts/run_with_validation.sh for detailed setup"
        exit 1
    fi
else
    MODEL="wav2lip"
fi

echo "🌐 Server will be available at:"
echo "   👤 Dashboard: http://localhost:8010/dashboard.html"
echo "   🔗 WebRTC API: http://localhost:8010/webrtcapi.html"
echo ""
echo "📝 Usage:"
echo "   1. Open the dashboard URL in your browser"
echo "   2. Click 'Start Connection' to begin"
echo "   3. Use chat mode to interact with the avatar"
echo ""
echo "🛑 Press Ctrl+C to stop the server"
echo ""

# Start with minimal arguments
python app.py --model "$MODEL" --avatar_id avator_1