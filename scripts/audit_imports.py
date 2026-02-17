#!/usr/bin/env python3
"""Audit cross-module imports and flag architecture layer violations.

Uses AST parsing to avoid false positives from string literals.

Architecture layers:
  - Infrastructure: logging_monitoring, validation, events, config_management, exceptions, utils
  - Core:           agents, coding, security
  - Specialized:    cerebrum, meme, bio_simulation, finance, quantum, spatial, embodiment, evolutionary_ai
  - Application:    cli, api, website, orchestrator

Rules:
  1. Infrastructure may NOT import Core or Specialized.
  2. Core may NOT import Specialized.
  3. Specialized may import Core and Infrastructure.
  4. Application may import anything.

Usage:
    python scripts/audit_imports.py [--json]
"""
import argparse
import ast
import json
import os
import sys
from pathlib import Path

SRC = Path(__file__).resolve().parent.parent / "src" / "codomyrmex"

INFRA = {"logging_monitoring", "validation", "events", "config_management", "exceptions", "utils"}
CORE = {"agents", "coding", "security"}
SPECIALIZED = {
    "cerebrum", "meme", "bio_simulation", "finance", "quantum",
    "spatial", "embodiment", "evolutionary_ai", "market",
}
APPLICATION = {"cli", "api", "website", "orchestrator"}


def get_layer(module: str) -> str:
    if module in INFRA:
        return "infra"
    if module in CORE:
        return "core"
    if module in SPECIALIZED:
        return "specialized"
    if module in APPLICATION:
        return "application"
    return "other"


def extract_imports_ast(filepath: Path) -> list[str]:
    """Extract imported codomyrmex module names using AST (avoids string-literal false
    positives)."""
    try:
        source = filepath.read_text(encoding="utf-8", errors="replace")
        tree = ast.parse(source, str(filepath))
    except (SyntaxError, UnicodeDecodeError):
        return []

    modules = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            if node.module and node.module.startswith("codomyrmex."):
                parts = node.module.split(".")
                if len(parts) >= 2:
                    modules.append(parts[1])
        elif isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name.startswith("codomyrmex."):
                    parts = alias.name.split(".")
                    if len(parts) >= 2:
                        modules.append(parts[1])
    return modules


def scan_imports() -> list[dict]:
    """Scan all .py files and extract cross-module imports via AST."""
    edges = []
    for root, _dirs, files in os.walk(SRC):
        for fname in files:
            if not fname.endswith(".py"):
                continue
            fpath = Path(root) / fname
            rel = fpath.relative_to(SRC)
            parts = rel.parts
            if len(parts) < 2:
                continue
            src_module = parts[0]
            if src_module == "__pycache__":
                continue

            for dst_module in extract_imports_ast(fpath):
                if dst_module == src_module:
                    continue
                edges.append({
                    "src": src_module,
                    "dst": dst_module,
                    "file": str(rel),
                    "src_layer": get_layer(src_module),
                    "dst_layer": get_layer(dst_module),
                })
    return edges


def find_violations(edges: list[dict]) -> list[dict]:
    """Apply layer rules and return violations."""
    violations = []
    for edge in edges:
        src_l = edge["src_layer"]
        dst_l = edge["dst_layer"]
        reason = None

        if src_l == "infra" and dst_l in ("core", "specialized"):
            reason = f"Infrastructure '{edge['src']}' imports {dst_l} '{edge['dst']}'"
        elif src_l == "core" and dst_l == "specialized":
            reason = f"Core '{edge['src']}' imports specialized '{edge['dst']}'"

        if reason:
            violations.append({**edge, "reason": reason})

    return violations


def main():
    parser = argparse.ArgumentParser(description="Audit cross-module imports")
    parser.add_argument("--json", action="store_true", help="Output JSON")
    args = parser.parse_args()

    edges = scan_imports()
    violations = find_violations(edges)

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
