#!/usr/bin/env python3
"""
Digital Human - Main Entry Point

This is the main entry point for the Digital Human application.
It imports and runs the main function from the src package.
"""

import sys
import os

# Add the src directory to the path so we can import from it
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.join(ROOT_DIR, 'src')
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

if __name__ == "__main__":
    from src.api.server import main
    main()