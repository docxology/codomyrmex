#!/usr/bin/env python3
"""
Build Synthesis - Real Usage Examples

Demonstrates actual build capabilities:
- Build target creation
- Build environment check
- Build type enumeration
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
from codomyrmex.build_synthesis import (
    BuildManager,
    create_python_build_target,
    get_available_build_types,
    check_build_environment
)

def main():
    setup_logging()
    print_info("Running Build Synthesis Examples...")

    # 1. Build Manager & Types
    print_info("Enumerating build types...")
    try:
        types = get_available_build_types()
        print_success(f"  Available build types: {', '.join(t.value for t in types)}")
    except Exception as e:
        print_error(f"  Failed to get build types: {e}")

    # 2. Build Targets
    print_info("Creating Python build target...")
    try:
        target = create_python_build_target(
            name="codomyrmex-dist",
            source_path="src",
            output_path="dist/codomyrmex"
        )
        print_success(f"  Build target '{target.name}' created.")
    except Exception as e:
        print_error(f"  Failed to create build target: {e}")

    # 3. Environment Check
    print_info("Checking build environment...")
    try:
        if check_build_environment():
            print_success("  Build environment is ready.")
        else:
            print_info("  Build environment check returned False.")
    except Exception as e:
        print_info(f"  Build environment check demo: {e}")

    print_success("Build synthesis examples completed successfully")
    return 0

if __name__ == "__main__":
    sys.exit(main())
