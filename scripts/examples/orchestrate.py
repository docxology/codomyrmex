#!/usr/bin/env python3
"""
Thin Orchestrator: Examples Module
Demonstrates capabilities of the codomyrmex.examples module.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from codomyrmex.examples import *

def main():
    print("=== Examples Module Orchestrator ===")
    print("This orchestrator demonstrates the examples module capabilities.")
    print("Available exports:", dir())
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
