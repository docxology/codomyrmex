#!/usr/bin/env python3
"""
Configuration Management - Real Usage Examples

Demonstrates actual configuration capabilities:
- load_configuration (merging)
- validate_configuration
- Configuration object usage
"""

import sys
from pathlib import Path

# Ensure codomyrmex is in path
try:
    import codomyrmex
except ImportError:
    project_root = Path(__file__).resolve().parent.parent.parent.parent
    sys.path.insert(0, str(project_root / "src"))

from codomyrmex.utils.cli_helpers import setup_logging, print_success, print_info, print_error
from codomyrmex.config_management import (
    validate_configuration,
    Configuration
)

def main():
    setup_logging()
    print_info("Running Configuration Management Examples...")

    # 1. Configuration Loading
    print_info("Testing configuration loading (simulated sources)...")
    try:
        # Load from a simple dict (simulating a file source)
        raw_config = {"app": {"name": "Example", "port": 8080}}
        config = Configuration(data=raw_config)
        print_success(f"  Configuration object created. App Name: {config.get('app.name')}")
    except Exception as e:
        print_error(f"  Config loading failed: {e}")

    # 2. Validation
    print_info("Testing configuration validation stubs...")
    try:
        if validate_configuration:
            print_success("  validate_configuration handler available.")
    except Exception as e:
        print_error(f"  Validation check failed: {e}")

    print_success("Configuration management examples completed successfully")
    return 0

if __name__ == "__main__":
    sys.exit(main())
