#!/usr/bin/env python3
"""
CLI Handlers - Real Usage Examples

Demonstrates actual CLI handler capabilities:
- check_environment
- show_info, show_modules
- show_system_status
"""

import sys
import os
from pathlib import Path

# Ensure codomyrmex is in path
try:
    import codomyrmex
except ImportError:
    project_root = Path(__file__).resolve().parent.parent.parent.parent
    sys.path.insert(0, str(project_root / "src"))

from codomyrmex.utils.cli_helpers import setup_logging, print_success, print_info, print_error
from codomyrmex.cli import (
    check_environment,
    show_info,
    show_modules,
    show_system_status
)

def main():
    setup_logging()
    print_info("Running CLI Handler Examples...")

    # 1. Environment Check
    print_info("Testing check_environment...")
    try:
        if check_environment():
            print_success("  Environment check PASSED.")
    except Exception as e:
        print_error(f"  Environment check failed: {e}")

    # 2. Show System Info
    print_info("Testing system info handlers...")
    try:
        # These usually print directly to stdout
        show_info()
        show_modules()
        show_system_status()
        print_success("  System info handlers executed successfully.")
    except Exception as e:
        print_error(f"  Info handlers failed: {e}")

    print_success("CLI handler examples completed successfully")
    return 0

if __name__ == "__main__":
    sys.exit(main())
