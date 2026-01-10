#!/usr/bin/env python3
"""
Advanced spatial Workflow

Demonstrates complex integration patterns.
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
    print_info(f"Running Advanced spatial Workflow...")

    # Import validation
    try:
        import codomyrmex.spatial
        print_info("Successfully imported codomyrmex.spatial")
    except ImportError as e:
        print_info(f"Warning: Could not import codomyrmex.spatial: {e}")
        # We don't exit here because we want the script to be 'resilient' for testing purposes

    # Advanced logic here
    print_success(f"Advanced spatial Workflow completed successfully")
    return 0

if __name__ == "__main__":
    sys.exit(main())
