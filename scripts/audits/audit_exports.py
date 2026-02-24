#!/usr/bin/env python3
"""
scripts/audit_exports.py

Thin wrapper around codomyrmex.static_analysis.exports.
"""

import argparse
import json
import sys
from pathlib import Path

# Ensure src is in path
PROJ_ROOT = Path(__file__).resolve().parent.parent
SRC_DIR = PROJ_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

try:
    from codomyrmex.static_analysis.exports import audit_exports, get_modules
except ImportError as e:
    print(f"Error importing codomyrmex module: {e}")
    sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Audit module __all__ exports")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--root", type=Path, default=PROJ_ROOT, help="Project root directory")
    args = parser.parse_args()

    src_dir = args.root / "src" / "codomyrmex"
    
    findings = audit_exports(src_dir)

    if args.json:
        print(json.dumps(findings, indent=2))
    else:
        modules = get_modules(src_dir)
        ok = len(modules) - len(findings)
        print(f"Modules audited: {len(modules)}")
        print(f"  ✅ With __all__: {ok}")
        print(f"  ❌ Missing/empty __all__: {len(findings)}")
        if findings:
            print()
            for f in findings:
                print(f"  [{f['issue']}] {f['detail']}")

    sys.exit(1 if findings else 0)


if __name__ == "__main__":
    main()
