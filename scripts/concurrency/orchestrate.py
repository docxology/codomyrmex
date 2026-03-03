#!/usr/bin/env python3
"""Orchestrator for concurrency module scripts."""

import sys
from pathlib import Path

# Add project root and src to path for direct execution and import
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))

from codomyrmex.orchestrator.core import main as orchestrator_main

def main():
    # Auto-injected: Load configuration
    import yaml
    from pathlib import Path
    config_path = Path(__file__).resolve().parent.parent.parent / "config" / "concurrency" / "config.yaml"
    config_data = {}
    if config_path.exists():
        with open(config_path, "r") as f:
            config_data = yaml.safe_load(f) or {}
            print(f"Loaded config from {config_path.name}")

    """Run all concurrency scripts via the orchestrator."""
    current_dir = Path(__file__).resolve().parent

    # Configure arguments for orchestrator to target this directory
    args = [
        f"--scripts-dir={current_dir}",
        "--verbose",
        "--timeout=30"
    ]

    # Support filtering from command line
    if len(sys.argv) > 1:
        args.extend(sys.argv[1:])

    print(f"🚀 Running concurrency module orchestrator in {current_dir}...")

    try:
        return orchestrator_main(args)
    except Exception as e:
        print(f"❌ Orchestrator failed: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
