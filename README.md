# Digital Human
The Digital Human System.

### 🏗️ **Code Restructuring**
```
src/
├── api/          # Web API and server
├── core/         # Core components (BaseReal, WebRTC)
├── models/       # AI model implementations
├── services/     # External services (TTS, LLM)
└── utils/        # Utilities (logging, etc.)
```

### 🌍 **International TTS Services**
- **EdgeTTS** (Microsoft) - Default, free, multiple languages
- **FishTTS** - Open source TTS
- **GPT-SoVITS** - Voice cloning TTS
- **CosyVoice** - High quality TTS
- **XTTS** - Real-time TTS

## Quick Start

### 1. Installation
```bash
# Install dependencies
pip install -r requirements_clean.txt

# Or use the original requirements (includes all dependencies)
pip install -r requirements.txt
```

### 2. Configuration
```bash
# Set environment variables for LLM (optional)
export OPENAI_API_KEY="your-openai-key"

# For voice cloning TTS services, set up your TTS server
# See TTS service documentation for details
```

### 3. Run the Server
```bash
# Using the new clean entry point
python main.py

# Or with custom configuration
python main.py --model musetalk --tts edgetts --avatar_id avator_1
```

### 4. Access the Interface
- **Main Dashboard**: http://localhost:8010/dashboard.html
- **Simple WebRTC**: http://localhost:8010/webrtcapi.html

## Configuration Options

### Core Settings
```bash
--model {musetalk|wav2lip|ultralight}  # AI model to use
--avatar_id avator_1                   # Avatar in data/avatars/
--batch_size 16                        # Inference batch size
--fps 50                              # Audio frame rate (must be 50)
```

### TTS Settings
```bash
--tts edgetts                         # TTS service
--REF_FILE "en-US-AriaNeural"        # Voice ID/reference file
--REF_TEXT "Reference text"           # For voice cloning
--TTS_SERVER "http://localhost:9880"  # TTS server URL
```

### Transport Options
```bash
--transport webrtc                    # webrtc/rtcpush/virtualcam
--listenport 8010                     # Server port
--max_session 1                       # Max concurrent sessions
```

## TTS Service Setup

### EdgeTTS (Recommended - Free)
```bash
python main.py --tts edgetts --REF_FILE "en-US-AriaNeural"
```

Available voices: `en-US-AriaNeural`, `en-GB-SoniaNeural`, `en-AU-NatashaNeural`, etc.

### FishTTS
```bash
# Start FishTTS server first
# Then run:
python main.py --tts fishtts --TTS_SERVER "http://localhost:5000"
```

### XTTS
```bash
# Start XTTS server first
# Then run:
python main.py --tts xtts --TTS_SERVER "http://localhost:9000"
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

## Project Structure

### Original Files (Preserved)
- `app.py` - Original server (still functional)
- `ttsreal.py` - Original TTS (with China APIs)
- `basereal.py` - Original base class
- Model files: `lipreal.py`, `musereal.py`, `lightreal.py`

### New Clean Structure
- `main.py` - New entry point
- `src/api/server.py` - Clean server implementation
- `src/services/tts.py` - International TTS services only
- `src/core/base_real.py` - Clean base class
- `requirements_clean.txt` - Minimal dependencies

## Migration Guide

### From Original to Clean Version

1. **Update imports** (if using as library):
   ```python
   # Old
   from basereal import BaseReal
   from ttsreal import EdgeTTS
   
   # New
   from src.core.base_real import BaseReal
   from src.services.tts import EdgeTTS
   ```

2. **Update TTS configuration**:
   ```bash
   # Remove China-specific TTS
   # --tts tencent    # ❌ Removed
   # --tts doubao     # ❌ Removed
   
   # Use international alternatives
   --tts edgetts      # ✅ Free, multilingual
   --tts fishtts      # ✅ Open source
   ```

3. **Update voice references**:
   ```bash
   # Old (Chinese)
   --REF_FILE "zh-CN-YunxiaNeural"
   
   # New (English)
   --REF_FILE "en-US-AriaNeural"
   ```

## Development

### Running Both Versions
```bash
# Original version
python app.py

# Clean version
python main.py
```

### Adding New TTS Services
1. Implement in `src/services/tts.py`
2. Add to configuration choices in `src/api/server.py`
3. Update documentation

## Troubleshooting

### Common Issues
1. **Import errors**: Make sure `src/` is in Python path
2. **TTS service unavailable**: Check server URLs and service status
3. **Model loading errors**: Verify model files in `models/` directory
4. **Port conflicts**: Change `--listenport` if 8010 is in use

### Logging
Set log level for debugging:
```python
from src.utils.logger import setup_logger
logger = setup_logger(level=logging.DEBUG, log_file="debug.log")
```

## License

Apache License 2.0 - See LICENSE file for details.

## Contributing

This clean version maintains compatibility with the original while providing:
- ✅ Better code organization
- ✅ International accessibility
- ✅ Cleaner dependencies
- ✅ Improved documentation
