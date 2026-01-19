#!/usr/bin/env python3
"""
Thin Orchestrator: CLI Module
Demonstrates capabilities of the codomyrmex.cli module.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from codomyrmex.cli import *

def main():
    print("=== CLI Module Orchestrator ===")
    print("This orchestrator demonstrates the CLI module capabilities.")
    print("Available exports:", dir())
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
