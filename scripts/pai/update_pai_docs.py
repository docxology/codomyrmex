#!/usr/bin/env python3
"""
scripts/update_pai_docs.py

Thin wrapper around codomyrmex.documentation.pai.update_pai_docs.
"""

import argparse
from pathlib import Path
import sys

# Ensure src is in path
PROJ_ROOT = Path(__file__).resolve().parent.parent
SRC_DIR = PROJ_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

try:
    from codomyrmex.documentation.pai import update_pai_docs, MAX_STUB_LINES
except ImportError as e:
    print(f"Error importing codomyrmex module: {e}")
    sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Batch update stub PAI.md files")
    parser.add_argument("--apply", action="store_true", help="Apply changes (default: dry run)")
    parser.add_argument("--max-lines", type=int, default=MAX_STUB_LINES,
                        help=f"Maximum lines to consider as stub (default: {MAX_STUB_LINES})")
    parser.add_argument("--root", type=Path, default=PROJ_ROOT, help="Project root directory")
    args = parser.parse_args()

    src_dir = args.root / "src" / "codomyrmex"
    
    update_pai_docs(src_dir, apply=args.apply, max_lines=args.max_lines)


if __name__ == "__main__":
    main()
