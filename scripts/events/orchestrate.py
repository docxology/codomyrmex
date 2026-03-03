#!/usr/bin/env python3
"""
Orchestrator for the events module.
Discovers and runs all event-related scripts and examples.
"""

import sys
import os
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
    config_path = Path(__file__).resolve().parent.parent.parent / "config" / "events" / "config.yaml"
    config_data = {}
    if config_path.exists():
        with open(config_path, "r") as f:
            config_data = yaml.safe_load(f) or {}
            print(f"Loaded config from config/events/config.yaml")

if __name__ == "__main__":
    # Force the scripts directory to be this one
    current_dir = Path(__file__).resolve().parent

    # We remove any existing --scripts-dir to ensure we use the current one
    new_args = [arg for arg in sys.argv if not arg.startswith("--scripts-dir")]
    new_args.append(f"--scripts-dir={current_dir}")

    # Set default output dir if not provided
    if not any(arg.startswith("--output-dir") or arg == "-o" for arg in new_args):
        output_dir = current_dir.parent.parent / "output" / "events_orchestration"
        new_args.append(f"--output-dir={output_dir}")

    print(f"🎬 Starting events orchestrator in: {current_dir}")
    sys.exit(main(new_args[1:]))
