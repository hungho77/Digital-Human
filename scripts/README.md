# Digital Human - Launch Scripts

This directory contains convenient bash scripts for running the Digital Human application with different AI models and configurations.

## 📁 Available Scripts

### 🚀 Quick Start
```bash
./scripts/quick_start.sh
```
- **Purpose**: Fast startup with minimal configuration
- **Model**: Automatically selects best available model
- **Config**: Default settings (port 8010, EdgeTTS, avator_1)
- **Best for**: First-time users, quick testing

### 🔍 Validated Startup
```bash
./scripts/run_with_validation.sh [--model MODEL] [options]
```
- **Purpose**: Comprehensive validation before starting
- **Features**: Dependency check, model availability, auto-selection
- **Config**: Customizable with command-line options
- **Best for**: Production deployments, troubleshooting

### 🎭 Wav2Lip Model
```bash
./scripts/run_wav2lip.sh [options]
```
- **Purpose**: Run with Wav2Lip model (accurate lip-sync)
- **Quality**: High accuracy lip synchronization
- **Speed**: Moderate inference speed
- **Best for**: High-quality conversations, demos

### 🎨 MuseTalk Model  
```bash
./scripts/run_musetalk.sh [options]
```
- **Purpose**: Run with MuseTalk model (high-quality animation)
- **Quality**: Best overall facial animation quality
- **Speed**: Slower inference, higher resource usage
- **Requirements**: Additional model files and avatar preparation
- **Best for**: Highest quality presentations

### ⚡ Ultralight Model
```bash
./scripts/run_ultralight.sh [options]
```
- **Purpose**: Run with Ultralight model (fast inference)
- **Quality**: Good quality with optimized speed
- **Speed**: Fastest inference, lowest resource usage  
- **Best for**: Real-time interaction, resource-constrained systems

## 🛠 Common Options

All model-specific scripts support these options:

| Option | Default | Description |
|--------|---------|-------------|
| `--avatar AVATAR_ID` | avator_1 | Avatar to use |
| `--port PORT` | 8010 | Server port |
| `--tts TTS_SERVICE` | edgetts | TTS service |
| `--voice VOICE_ID` | en-US-AriaNeural | Voice for TTS |
| `--batch-size SIZE` | 16 | Inference batch size |
| `--help` | - | Show help message |

## 📝 Usage Examples

### Basic Usage
```bash
# Quick start (recommended for beginners)
./scripts/quick_start.sh

# Run specific model
./scripts/run_wav2lip.sh
```

### Advanced Usage
```bash
# Custom avatar and port
./scripts/run_wav2lip.sh --avatar my_avatar --port 8011

# Different TTS voice
./scripts/run_musetalk.sh --voice en-GB-SoniaNeural

# Performance tuning
./scripts/run_ultralight.sh --batch-size 8 --port 8012

# Full validation with custom config
./scripts/run_with_validation.sh --model wav2lip --avatar avator_1 --tts edgetts
```

## 🔧 Making Scripts Executable

Before first use, make the scripts executable:
```bash
chmod +x scripts/*.sh
```

## 🌐 Access Points

After starting any script, access the application at:
- **Dashboard**: http://localhost:8010/dashboard.html
- **WebRTC API**: http://localhost:8010/webrtcapi.html

(Replace 8010 with your custom port if specified)

## 📋 Model Requirements

| Model | Requirements |
|-------|--------------|
| **Wav2Lip** | `models/wav2lip/wav2lip.pth` |
| **MuseTalk** | `models/musetalkV15/unet.pth`<br>`models/musetalkV15/musetalk.json`<br>`data/avatars/*/latents.pt`<br>`data/avatars/*/mask/` |
| **Ultralight** | `models/ultralight/ultralight.pth` |

## ⚠️ Troubleshooting

### Script Not Found
```bash
# Make sure you're in the project root
cd Digital-Human
./scripts/run_wav2lip.sh
```

### Permission Denied
```bash
# Make scripts executable
chmod +x scripts/*.sh
```

### Model Files Missing
```bash
# Use validation script to check
./scripts/run_with_validation.sh
```

### Port Already in Use
```bash
# Use different port
./scripts/run_wav2lip.sh --port 8011
```

## 🆘 Getting Help

Each script has built-in help:
```bash
./scripts/run_wav2lip.sh --help
./scripts/run_musetalk.sh --help
./scripts/run_ultralight.sh --help
./scripts/run_with_validation.sh --help
```

For more detailed documentation, see the main [README.md](../README.md).