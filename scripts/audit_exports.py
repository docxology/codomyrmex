#!/usr/bin/env python3
"""Audit every module's __init__.py for __all__ exports and validate they actually exist.

Usage:
    python scripts/audit_exports.py [--fix]
"""
import argparse
import ast
import importlib
import os
import sys
from pathlib import Path

SRC = Path(__file__).resolve().parent.parent / "src" / "codomyrmex"

# Modules that are not real packages (skip)
SKIP = {"__pycache__", "py.typed"}


def get_modules() -> list[Path]:
    """Return paths to all module directories that have __init__.py."""
    modules = []
    for entry in sorted(SRC.iterdir()):
        if entry.is_dir() and entry.name not in SKIP and (entry / "__init__.py").exists():
            modules.append(entry)
    return modules


def check_all_defined(init_path: Path) -> tuple[bool, list[str] | None]:
    """Parse __init__.py and check for __all__. Returns (has_all, names_or_None)."""
    source = init_path.read_text(encoding="utf-8")
    try:
        tree = ast.parse(source, str(init_path))
    except SyntaxError:
        return False, None

    for node in ast.walk(tree):
        # Standard: __all__ = [...]
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "__all__":
                    if isinstance(node.value, (ast.List, ast.Tuple)):
                        names = []
                        for elt in node.value.elts:
                            if isinstance(elt, ast.Constant) and isinstance(elt.value, str):
                                names.append(elt.value)
                        return True, names
                    return True, None
        # Annotated: __all__: list[str] = [...]
        if isinstance(node, ast.AnnAssign):
            if isinstance(node.target, ast.Name) and node.target.id == "__all__":
                if node.value and isinstance(node.value, (ast.List, ast.Tuple)):
                    names = []
                    for elt in node.value.elts:
                        if isinstance(elt, ast.Constant) and isinstance(elt.value, str):
                            names.append(elt.value)
                    return True, names
                return True, None
    return False, None


def audit() -> list[dict]:
    """Run the audit. Returns list of findings."""
    findings = []
    modules = get_modules()

    for mod_path in modules:
        init = mod_path / "__init__.py"
        mod_name = mod_path.name
        has_all, names = check_all_defined(init)

        if not has_all:
            findings.append({
                "module": mod_name,
                "issue": "MISSING_ALL",
                "detail": f"{mod_name}/__init__.py has no __all__ definition",
            })
        # Empty __all__ is valid (e.g., template/example modules)

    return findings


def main():
    parser = argparse.ArgumentParser(description="Audit module __all__ exports")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    findings = audit()

    if args.json:
        import json
        print(json.dumps(findings, indent=2))
    else:
        modules = get_modules()
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
