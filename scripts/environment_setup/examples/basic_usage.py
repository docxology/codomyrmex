#!/usr/bin/env python3
"""
Environment Setup - Real Usage Examples

Demonstrates actual environment capabilities:
- Python version validation
- UV environment detection
- Environmental variable check
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
from codomyrmex.environment_setup import (
    validate_python_version,
    is_uv_available,
    is_uv_environment,
    check_and_setup_env_vars
)

def main():
    setup_logging()
    print_info("Running Environment Setup Examples...")

    # 1. Python Version
    print_info("Validating Python version...")
    if validate_python_version():
        print_success("  Python version is compatible.")
    else:
        print_info("  Python version validation returned False.")

    # 2. UV Tooling
    print_info("Checking for UV Availability...")
    if is_uv_available():
        print_success("  UV tool is found.")
    else:
        print_info("  UV tool not found.")

    if is_uv_environment():
        print_success("  Running inside a UV-managed environment.")
    else:
        print_info("  Not in a UV-managed environment.")

    # 3. Env Vars
    print_info("Running check_and_setup_env_vars...")
    try:
        # project_root is defined above but might need to be recalculated or passed
        current_project_root = str(Path(__file__).resolve().parent.parent.parent.parent)
        check_and_setup_env_vars(current_project_root)
        print_success("  Environment variables check completed.")
    except Exception as e:
        print_info(f"  Env vars check demo: {e}")

    print_success("Environment setup examples completed successfully")
    return 0

if __name__ == "__main__":
    sys.exit(main())
