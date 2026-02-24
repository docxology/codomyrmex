#!/usr/bin/env python3
"""
scripts/audit_imports.py

Thin wrapper around codomyrmex.static_analysis.imports.
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
    from codomyrmex.static_analysis.imports import scan_imports, check_layer_violations
except ImportError as e:
    print(f"Error importing codomyrmex module: {e}")
    sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Audit cross-module imports")
    parser.add_argument("--json", action="store_true", help="Output JSON")
    parser.add_argument("--root", type=Path, default=PROJ_ROOT, help="Project root directory")
    args = parser.parse_args()

    src_dir = args.root / "src" / "codomyrmex"
    if not src_dir.exists():
        print(f"Error: Source directory {src_dir} does not exist.")
        sys.exit(1)

    edges = scan_imports(src_dir)
    violations = check_layer_violations(edges)

    unique_edges = {}
    for e in edges:
        key = (e["src"], e["dst"])
        unique_edges[key] = unique_edges.get(key, 0) + 1

    unique_violations = {}
    for v in violations:
        key = (v["src"], v["dst"])
        if key not in unique_violations:
            unique_violations[key] = {"count": 0, "reason": v["reason"], "files": []}
        unique_violations[key]["count"] += 1
        unique_violations[key]["files"].append(v["file"])

    if args.json:
        print(json.dumps({
            "total_edges": len(unique_edges),
            "violations": [
                {"src": k[0], "dst": k[1], **v}
                for k, v in unique_violations.items()
            ]
        }, indent=2))
    else:
        print(f"Import edges: {len(unique_edges)}")
        print(f"Violations:   {len(unique_violations)}")
        if unique_violations:
            print()
            for (src, dst), info in sorted(unique_violations.items()):
                print(f"  ❌ {src} → {dst} ({info['count']} files)")
                print(f"     {info['reason']}")
        else:
            print("  ✅ No cross-layer violations found")

    sys.exit(1 if unique_violations else 0)


if __name__ == "__main__":
    main()
