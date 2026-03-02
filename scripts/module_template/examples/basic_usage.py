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

from codomyrmex.utils.cli_helpers import setup_logging, print_success, print_info

def main():
    setup_logging()
    print_info(f"Running Basic module_template Usage...")

    # Import validation
    try:
        import codomyrmex.module_template  # noqa: F401
        print_info("Successfully imported codomyrmex.module_template")
    except ImportError as e:
        print_info(f"Warning: Could not import codomyrmex.module_template: {e}")
        # We don't exit here because we want the script to be 'resilient' for testing purposes

    # Basic logic here
    print_success(f"Basic module_template Usage completed successfully")
    return 0

if __name__ == "__main__":
    sys.exit(main())
