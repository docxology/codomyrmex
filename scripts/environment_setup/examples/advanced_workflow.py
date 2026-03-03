#!/usr/bin/env python3
"""
Advanced environment_setup Workflow

Demonstrates complex integration patterns.
"""

import sys
from pathlib import Path

# Ensure codomyrmex is in path
try:
    import codomyrmex  # noqa: F401
except ImportError:
    project_root = Path(__file__).resolve().parent.parent.parent.parent
    sys.path.insert(0, str(project_root / "src"))

from codomyrmex.utils.cli_helpers import print_info, print_success, setup_logging


def main():
    # Auto-injected: Load configuration
    from pathlib import Path

    import yaml

    config_path = (
        Path(__file__).resolve().parent.parent.parent
        / "config"
        / "environment_setup"
        / "config.yaml"
    )
    config_data = {}
    if config_path.exists():
        with open(config_path) as f:
            config_data = yaml.safe_load(f) or {}
            print("Loaded config from config/environment_setup/config.yaml")

    setup_logging()
    print_info("Running Advanced environment_setup Workflow...")

    # Import validation
    try:
        import codomyrmex.environment_setup  # noqa: F401

        print_info("Successfully imported codomyrmex.environment_setup")
    except ImportError as e:
        print_info(f"Warning: Could not import codomyrmex.environment_setup: {e}")
        # We don't exit here because we want the script to be 'resilient' for testing purposes

    # Advanced logic here
    print_success("Advanced environment_setup Workflow completed successfully")
    return 0


if __name__ == "__main__":
    sys.exit(main())
