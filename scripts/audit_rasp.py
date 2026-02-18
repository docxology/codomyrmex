#!/usr/bin/env python3
"""
scripts/audit_rasp.py

Thin wrapper around codomyrmex.documentation.audit.audit_rasp.
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
    from codomyrmex.documentation.audit import audit_rasp
except ImportError as e:
    print(f"Error importing codomyrmex module: {e}")
    print("Ensure you are running from the project root or have set PYTHONPATH.")
    sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Audit RASP documentation breadth.")
    parser.add_argument("--root", type=Path, default=PROJ_ROOT, help="Project root directory")
    args = parser.parse_args()
    
    src_dir = args.root / "src" / "codomyrmex"
    
    if not src_dir.exists():
        print(f"Critical Error: Could not find src/codomyrmex at {src_dir}")
        sys.exit(1)
        
    sys.exit(audit_rasp(src_dir))


if __name__ == "__main__":
    main()
