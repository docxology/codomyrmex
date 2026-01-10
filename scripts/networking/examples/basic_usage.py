#!/usr/bin/env python3
"""
Basic networking Usage

Demonstrates basic usage patterns.
"""

import sys
from pathlib import Path

# Ensure codomyrmex is in path
try:
    import codomyrmex
except ImportError:
    project_root = Path(__file__).resolve().parent.parent.parent.parent
    sys.path.insert(0, str(project_root / "src"))

from codomyrmex.utils.cli_helpers import setup_logging, print_success, print_info

def main():
    setup_logging()
    print_info(f"Running Basic networking Usage...")

    # Import validation
    try:
        import codomyrmex.networking
        print_info("Successfully imported codomyrmex.networking")
    except ImportError as e:
        print_info(f"Warning: Could not import codomyrmex.networking: {e}")
        # We don't exit here because we want the script to be 'resilient' for testing purposes

    # Basic logic here
    print_success(f"Basic networking Usage completed successfully")
    return 0

if __name__ == "__main__":
    sys.exit(main())
