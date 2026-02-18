#!/usr/bin/env python3
"""
scripts/validate_pai_integration.py

Thin wrapper around codomyrmex.validation.pai.validate_pai_integration.
"""

import sys
from pathlib import Path

# Ensure src is in path
PROJ_ROOT = Path(__file__).resolve().parent.parent
SRC_DIR = PROJ_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

try:
    from codomyrmex.validation.pai import validate_pai_integration
except ImportError as e:
    print(f"Error importing codomyrmex module: {e}")
    sys.exit(1)


def main():
    src_dir = PROJ_ROOT / "src" / "codomyrmex"
    sys.exit(validate_pai_integration(src_dir))


if __name__ == "__main__":
    main()
