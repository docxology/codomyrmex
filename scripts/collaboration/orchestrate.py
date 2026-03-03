#!/usr/bin/env python3
"""Orchestrator for collaboration module scripts.

This script discovers and runs all scripts in the collaboration module directory.

Usage:
    python orchestrate.py [--timeout SECONDS]
"""

import sys
from pathlib import Path

# Ensure codomyrmex is in path
try:
    import codomyrmex  # noqa: F401
except ImportError:
    project_root = Path(__file__).resolve().parent.parent.parent
    sys.path.insert(0, str(project_root / "src"))

from codomyrmex.orchestrator.core import main


    # Auto-injected: Load configuration
    import yaml
    from pathlib import Path
    config_path = Path(__file__).resolve().parent.parent.parent / "config" / "collaboration" / "config.yaml"
    config_data = {}
    if config_path.exists():
        with open(config_path, "r") as f:
            config_data = yaml.safe_load(f) or {}
            print(f"Loaded config from config/collaboration/config.yaml")

if __name__ == "__main__":
    # Run the orchestrator for this specific module directory
    current_dir = Path(__file__).resolve().parent
    if not any(arg.startswith("--scripts-dir") for arg in sys.argv):
        sys.argv.append(f"--scripts-dir={current_dir}")
    sys.exit(main())
