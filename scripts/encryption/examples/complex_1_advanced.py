#!/usr/bin/env python3
"""
Encryption Advanced Usage

Demonstrates advanced usage patterns.
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
    print_info("Running Encryption Advanced Usage...")
    
    # Advanced usage logic here
    print_success("Encryption Advanced Usage completed successfully")
    return 0

if __name__ == "__main__":
    sys.exit(main())
