# Digital Human - Real-time AI Avatar

A fully functional real-time digital human application with AI lip-sync animation, voice synthesis, and WebRTC streaming.

## ✅ Current Status

**WORKING** - The application has been successfully refactored and tested:
- ✅ **WebRTC Streaming**: Real-time video/audio streaming functional
- ✅ **AI Models**: wav2lip model working with accurate lip-sync
- ✅ **TTS Integration**: EdgeTTS and other TTS services working
- ✅ **Avatar System**: Default avatar rendering and animation
- ✅ **Web Interface**: Dashboard and API endpoints fully functional
- ✅ **Session Management**: Multi-session support working

## ✨ Features

- **3 AI Models**: MuseTalk, Wav2Lip, and Ultralight for different animation styles
- **Real-time Streaming**: WebRTC-based video/audio streaming
- **Multi-language TTS**: EdgeTTS, FishTTS, GPT-SoVITS, CosyVoice, XTTS
- **Interactive Chat**: AI conversation with lip-sync animation
- **Avatar System**: Configurable avatars and expressions
- **Web Interface**: Dashboard and WebRTC API endpoints

## 🏗️ Architecture
```
src/
├── api/           # Web server and API endpoints
├── core/          # Base classes (BaseReal, BaseASR)  
├── modules/       # AI model implementations
│   ├── musetalk/  # MuseTalk model for high-quality animation
│   ├── wav2lip/   # Wav2Lip model for accurate lip-sync
│   └── ultralight/# Ultralight model for fast inference
├── services/      # External services (TTS, LLM, WebRTC, unified service)
└── utils/         # Utilities (logging, etc.)
```

### 🌍 **International TTS Services**
- **EdgeTTS** (Microsoft) - Default, free, multiple languages
- **FishTTS** - Open source TTS
- **GPT-SoVITS** - Voice cloning TTS
- **CosyVoice** - High quality TTS
- **XTTS** - Real-time TTS

## 🚀 Quick Start

### 1. Installation
```bash
# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration (Optional)
```bash
# Set environment variables for LLM
export OPENAI_API_KEY="your-openai-key"

# For voice cloning TTS services, set up your TTS server
# See TTS service documentation for details
```

### 3. Run the Application

#### Option A: Using Launch Scripts (Recommended)
```bash
# Quick start with automatic model selection
./scripts/quick_start.sh

# Run specific models
./scripts/run_wav2lip.sh
./scripts/run_musetalk.sh  
./scripts/run_ultralight.sh

# Run with full validation
./scripts/run_with_validation.sh
```

#### Option B: Direct Python Commands
```bash
# Recommended: Run with validation
python run.py

# Or run directly with options
python app.py --model wav2lip --avatar_id avator_1
```

### 4. Access the Interface
- **Main Dashboard**: http://localhost:8010/dashboard.html
- **WebRTC API**: http://localhost:8010/webrtcapi.html

### 5. Start Interaction
1. Open the dashboard in your browser
2. Click **"Start Connection"** to initiate WebRTC streaming
3. You should see the avatar appear immediately in idle state
4. Use the chat interface to interact with the Digital Human

## Configuration Options

### Available Models
```bash
--model musetalk      # High-quality facial animation (default)
--model wav2lip       # Accurate lip-sync animation
--model ultralight    # Fast inference for real-time
```

### Avatar Configuration
```bash
--avatar_id avator_1  # Avatar in data/avatars/ directory
--batch_size 16       # Inference batch size
--fps 50             # Audio frame rate (must be 50)
```

### TTS Configuration
```bash
--tts edgetts                         # TTS service (edgetts/fishtts/xtts/etc.)
--REF_FILE "en-US-AriaNeural"        # Voice ID/reference file
--REF_TEXT "Reference text"           # For voice cloning
--TTS_SERVER "http://localhost:9880"  # TTS server URL
```

### Server Options
```bash
--transport webrtc    # Transport method (webrtc/rtcpush/virtualcam)
--listenport 8010     # Server port
--max_session 1       # Max concurrent sessions
```

## TTS Service Setup

### EdgeTTS (Recommended - Free)
```bash
python app.py --tts edgetts --REF_FILE "en-US-AriaNeural"
```

Available voices: `en-US-AriaNeural`, `en-GB-SoniaNeural`, `en-AU-NatashaNeural`, etc.

### FishTTS
```bash
# Start FishTTS server first, then run:
python app.py --tts fishtts --TTS_SERVER "http://localhost:5000"
```

### XTTS
```bash
# Start XTTS server first, then run:
python app.py --tts xtts --TTS_SERVER "http://localhost:9000"
```

## API Endpoints

### Chat/Echo
```javascript
POST /human
{
    "sessionid": 123456,
    "type": "chat",        // or "echo"
    "text": "Hello world",
    "interrupt": false     // optional
}
```

### Audio Upload
```javascript
POST /humanaudio
// Multipart form with audio file
```

### Recording
```javascript
POST /record
{
    "sessionid": 123456,
    "type": "start_record"  // or "end_record"
}
```

### Status Check
```javascript
POST /is_speaking
{
    "sessionid": 123456
}
```

## 📁 Project Structure

```
Digital-Human/
├── app.py                 # Main application entry point
├── run.py                 # Startup validation and runner
├── requirements.txt       # Dependencies
├── scripts/              # Launch scripts for different models
│   ├── quick_start.sh    # Fast startup with auto-detection
│   ├── run_wav2lip.sh    # Launch with Wav2Lip model
│   ├── run_musetalk.sh   # Launch with MuseTalk model
│   ├── run_ultralight.sh # Launch with Ultralight model
│   ├── run_with_validation.sh # Full validation startup
│   └── README.md         # Scripts documentation
├── data/
│   ├── avatars/          # Avatar configurations
│   └── models/           # AI model files
├── src/
│   ├── api/             # Web server and API endpoints
│   │   ├── server.py    # FastAPI server
│   │   └── static/      # Web UI files
│   ├── core/            # Base classes and core components
│   │   ├── base_real.py # Base class for AI models
│   │   └── asr_base.py  # ASR base class
│   ├── modules/         # AI model implementations
│   │   ├── musetalk/    # MuseTalk model
│   │   ├── wav2lip/     # Wav2Lip model
│   │   └── ultralight/  # Ultralight model
│   ├── services/        # External services
│   │   ├── tts.py       # TTS services
│   │   ├── llm.py       # LLM integration
│   │   ├── webrtc.py    # WebRTC streaming
│   │   └── unified_real.py # Unified service manager
│   └── utils/           # Utilities
│       └── logger.py    # Logging configuration
├── web/                 # Web interface files
│   ├── dashboard.html   # Main dashboard
│   ├── webrtcapi.html   # WebRTC API interface
│   └── client.js        # WebRTC client code
└── configs/             # Configuration files
    └── avatar_config.yaml
```

## 🔧 Development

### Adding New TTS Services
1. Implement in `src/services/tts.py`
2. Add to configuration choices in `src/api/server.py` 
3. Update this documentation

### Adding New AI Models
1. Create new module in `src/modules/`
2. Inherit from `BaseReal` in `src/core/base_real.py`
3. Register in `src/services/unified_real.py`

### Code Architecture
- **Modular Design**: Each AI model is a separate module
- **Service Layer**: Clean separation between models and external services
- **Unified Interface**: Single entry point manages all models and services
- **Configuration Driven**: Avatar and model settings via config files

## 🐛 Troubleshooting

### Common Issues

1. **Import errors**: 
   ```bash
   # Make sure you're in the project root directory
   cd Digital-Human
   python app.py
   ```

2. **Model loading errors**: 
   - Verify model files exist in `data/models/` directory
   - Check that model files are properly downloaded and placed

3. **WebRTC Connection Issues**:
   - **"Connecting..." stuck**: Refresh browser and try again
   - **No video showing**: Ensure STUN server is enabled (checkbox in dashboard)
   - **Browser compatibility**: Use Chrome/Firefox, avoid Safari for WebRTC
   - **HTTPS requirement**: Some browsers require HTTPS for WebRTC (use `--ssl` flag)
   - **Console errors**: Open browser dev tools (F12) to check for JavaScript errors

4. **TTS service unavailable**:
   - For EdgeTTS: Check internet connection (no server needed)
   - For other TTS: Verify server URLs and service status

5. **Port conflicts**: 
   ```bash
   # Change port if 8010 is in use
   python app.py --listenport 8011
   ```

6. **Avatar not found**:
   - Ensure avatar files exist in `data/avatars/avator_1/`
   - Check avatar configuration in `configs/avatar_config.yaml`

### Dependencies Check
```bash
# Run validation to check all dependencies
python run.py --check-only
```

### Debug Mode
Enable detailed logging:
```bash
python app.py --debug
```

## 📄 License

Apache License 2.0 - See LICENSE file for details.

## 🤝 Contributing

This refactored version provides:
- ✅ Clean modular architecture
- ✅ Multiple AI model support  
- ✅ International TTS services
- ✅ Real-time WebRTC streaming
- ✅ Comprehensive documentation
- ✅ Production-ready code structure

## 🔧 Technical Notes

### WebRTC Fixes Applied
The following critical fixes were implemented to ensure reliable WebRTC streaming:

1. **Idle Frame Generation**: Modified inference engine to generate default avatar frames even when no audio input is present, preventing "Connecting..." state
2. **STUN Server Configuration**: Enabled Google STUN server by default for better NAT traversal
3. **Audio Element**: Added missing HTML audio element for proper WebRTC track handling
4. **Enhanced Debugging**: Comprehensive console logging for WebRTC connection troubleshooting
5. **Error Handling**: Improved error handling for autoplay restrictions and connection failures

### Dependency Compatibility
- **PyTorch 2.7.1+**: Latest stable version with improved performance
- **Transformers 4.55.0+**: Latest version with better model compatibility
- **aiortc 1.13.0+**: Stable WebRTC implementation for Python
- **Edge-TTS 7.2.0+**: Latest Microsoft TTS service integration

### Architecture Improvements
- **Dynamic Model Loading**: Conditional imports prevent dependency conflicts
- **Unified Service Layer**: Clean abstraction for model management
- **Modular Design**: Easy to extend with new models and TTS services
