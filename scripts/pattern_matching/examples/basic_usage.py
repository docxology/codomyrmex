#!/usr/bin/env python3
"""
Basic pattern_matching Usage

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
        / "pattern_matching"
        / "config.yaml"
    )
    config_data = {}
    if config_path.exists():
        with open(config_path) as f:
            config_data = yaml.safe_load(f) or {}
            print("Loaded config from config/pattern_matching/config.yaml")

    setup_logging()
    print_info("Running Basic pattern_matching Usage...")

    # 1. Pattern Matching Analysis
    print_info("Testing Pattern Matching initialization...")
    try:
        from codomyrmex.pattern_matching import get_embedding_function

        # Test embedding function if available
        try:
            embedder = get_embedding_function()
            if embedder:
                print_success("  Embedding function initialized successfully.")
        except Exception as e:
            print_info(f"  Embedder initialization note: {e}")

        print_success("  Pattern matching module ready for analysis.")
    except Exception as e:
        print_error(f"  Pattern matching flow failed: {e}")

    print_success("Pattern matching Usage completed successfully")
    return 0


if __name__ == "__main__":
    sys.exit(main())
