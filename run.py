#!/usr/bin/env python3
"""
Digital Human - Startup Script with Dependency Checking

This script checks for required dependencies before starting the application.
"""

import sys
import os
import importlib

# Add the src directory to the path
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.join(ROOT_DIR, 'src')
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

def check_dependencies():
    """Check if required dependencies are available"""
    required_packages = [
        'torch',
        'numpy',
        'cv2',
        'aiohttp',
        'aiohttp_cors',
        'aiortc',
        'av',
        'tqdm',
        'transformers'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            importlib.import_module(package)
            print(f"✓ {package}")
        except ImportError:
            missing_packages.append(package)
            print(f"✗ {package} - MISSING")
    
    if missing_packages:
        print(f"\nMissing {len(missing_packages)} required packages:")
        for pkg in missing_packages:
            print(f"  - {pkg}")
        print("\nPlease install missing packages with:")
        print("  pip install -r requirements.txt")
        return False
    
    print("\n✓ All required dependencies are available!")
    return True

def check_avatar_data():
    """Check if avatar data is available"""
    avatar_path = "./data/avatars/avator_1"
    required_files = [
        "coords.pkl",
        "full_imgs", 
        "face_imgs"
    ]
    
    print("\n--- Checking Avatar Data ---")
    
    if not os.path.exists(avatar_path):
        print(f"✗ Avatar directory not found: {avatar_path}")
        return False
        
    missing_files = []
    for file_path in required_files:
        full_path = os.path.join(avatar_path, file_path)
        if os.path.exists(full_path):
            print(f"✓ {file_path}")
        else:
            missing_files.append(file_path)
            print(f"✗ {file_path} - MISSING")
    
    if missing_files:
        print(f"\nMissing {len(missing_files)} required avatar files/directories")
        return False
    
    # Check for model-specific files (optional warnings)
    optional_files = {
        "latents.pt": "MuseTalk",
        "mask": "MuseTalk", 
        "mask_coords.pkl": "MuseTalk",
        "ultralight.pth": "Ultralight"
    }
    
    print("\n--- Optional Model-Specific Files ---")
    for file_path, model_name in optional_files.items():
        full_path = os.path.join(avatar_path, file_path)
        if os.path.exists(full_path):
            print(f"✓ {file_path} ({model_name})")
        else:
            print(f"⚠ {file_path} ({model_name}) - Missing (will cause error if using {model_name})")
    
    return True

def check_model_files():
    """Check if model files are available"""
    print("\n--- Checking Model Files ---")
    
    model_files = [
        "./models/whisper/tiny.pt",
        "./models/wav2lip/wav2lip.pth"
    ]
    
    for model_file in model_files:
        if os.path.exists(model_file):
            print(f"✓ {model_file}")
        else:
            print(f"⚠ {model_file} - Missing")
    
    # Check for MuseTalk models (directory)
    musetalk_path = "./models/musetalkV15"
    if os.path.exists(musetalk_path) and os.path.isdir(musetalk_path):
        print(f"✓ {musetalk_path}")
    else:
        print(f"⚠ {musetalk_path} - Missing")
    
    return True

def main():
    """Main startup function"""
    print("=== Digital Human Startup Check ===\n")
    
    print("--- Checking Dependencies ---")
    deps_ok = check_dependencies()
    
    avatar_ok = check_avatar_data()
    check_model_files()  # Just check and warn, don't block startup
    
    if not deps_ok:
        print("\n❌ Cannot start: Missing required dependencies")
        sys.exit(1)
    
    if not avatar_ok:
        print("\n❌ Cannot start: Missing required avatar data") 
        print("Please ensure avatar data is properly set up in ./data/avatars/avator_1/")
        sys.exit(1)
        
    print("\n--- Starting Application ---")
    try:
        from src.api.server import main as server_main
        server_main()
    except Exception as e:
        print(f"❌ Failed to start server: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()