#!/usr/bin/env python3
"""
scripts/audit_documentation.py

Thin wrapper around codomyrmex.documentation.audit.audit_documentation.
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
    from codomyrmex.documentation.quality.audit import audit_documentation
except ImportError as e:
    print(f"Error importing codomyrmex module: {e}")
    print("Ensure you are running from the project root or have set PYTHONPATH.")
    sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Audit documentation completeness.")
    parser.add_argument("--root", type=Path, default=PROJ_ROOT, help="Project root directory")
    parser.add_argument("--report", type=Path, default=None, help="Output path for the report file")
    
    args = parser.parse_args()
    
    root_dir = args.root
    src_dir = root_dir / "src" / "codomyrmex"
    report_file = args.report or (root_dir / "docs_audit_report.md")
    
    audit_documentation(src_dir, report_file)


if __name__ == "__main__":
    main()
