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
    # Auto-injected: Load configuration
    from pathlib import Path

    import yaml
    config_path = Path(__file__).resolve().parent.parent.parent / "config" / "examples" / "config.yaml"
    config_data = {}
    if config_path.exists():
        with open(config_path) as f:
            config_data = yaml.safe_load(f) or {}
            print(f"Loaded config from {config_path.name}")

    print("=== Examples Module Orchestrator ===")
    print("This orchestrator demonstrates the examples module capabilities.")
    print("Available exports:", dir())
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
