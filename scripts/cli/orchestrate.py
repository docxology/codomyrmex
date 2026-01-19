#!/usr/bin/env python3
"""
Thin Orchestrator: CLI Module
Demonstrates capabilities of the codomyrmex.cli module.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from codomyrmex.cli import *

from codomyrmex.cli import show_info, show_modules

def main():
    print("=== CLI Module Orchestrator ===")
    print("Visualizing system information using real CLI handlers...")
    
    # 1. Show system information
    show_info()
    
    # 2. Show available modules
    print("\n--- Available Modules ---")
    show_modules()
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
