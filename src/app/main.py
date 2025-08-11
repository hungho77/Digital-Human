#!/usr/bin/env python3
"""
Digital Human - Main Entry Point

"""

import sys
import os

# Ensure project root src/ and src/modules are in sys.path
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
MODULES = os.path.join(ROOT, "modules")
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
if MODULES not in sys.path:
    sys.path.insert(0, MODULES)

from src.api.server import main

if __name__ == "__main__":
    main()
