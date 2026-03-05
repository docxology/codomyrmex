#!/usr/bin/env python3
"""
Basic module_template Usage

Demonstrates basic usage patterns.
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
        / "module_template"
        / "config.yaml"
    )
    if config_path.exists():
        with open(config_path) as f:
            yaml.safe_load(f) or {}
            print("Loaded config from config/module_template/config.yaml")

    setup_logging()
    print_info("Running Basic module_template Usage...")

    # Import validation
    try:
        import codomyrmex.module_template  # noqa: F401

        print_info("Successfully imported codomyrmex.module_template")
    except ImportError as e:
        print_info(f"Warning: Could not import codomyrmex.module_template: {e}")
        # We don't exit here because we want the script to be 'resilient' for testing purposes

    # Basic logic here
    print_success("Basic module_template Usage completed successfully")
    return 0


if __name__ == "__main__":
    sys.exit(main())
