#!/usr/bin/env python3
"""
scripts/fix_missing_docstrings.py

Prepends docstrings to __init__.py files that are missing them.
Targeted at a specific list of modules identified in the audit.
"""

import sys
import argparse
from pathlib import Path
import ast

# Default list of relative paths to packages that are missing docstrings
DEFAULT_TARGETS = [
    "documentation/scripts",
    "tests/unit/tools",
    "tests/unit/api",
    "agents/core",
    "agents/cli",
    "agents/git_agent",
    "cli/handlers",
    "cerebrum/visualization",
    "cerebrum/core",
    "cerebrum/inference",
    "cerebrum/fpf",
]

DOCSTRINGS = {
    "documentation/scripts": '"""Documentation generation scripts."""\n',
    "tests/unit/tools": '"""Unit tests for tools module."""\n',
    "tests/unit/api": '"""Unit tests for API module."""\n',
    "agents/core": '"""Core agent infrastructure and base classes."""\n',
    "agents/cli": '"""CLI agent implementation."""\n',
    "agents/git_agent": '"""Git operations agent."""\n',
    "cli/handlers": '"""CLI command handlers."""\n',
    "cerebrum/visualization": '"""Visualization tools for Cerebrum reasoning engine."""\n',
    "cerebrum/core": '"""Core Cerebrum reasoning logic and engine."""\n',
    "cerebrum/inference": '"""Inference mechanisms for Cerebrum."""\n',
    "cerebrum/fpf": '"""First Principles Framework integration for Cerebrum."""\n',
}

def has_docstring(file_path: Path) -> bool:
    try:
        tree = ast.parse(file_path.read_text())
        return ast.get_docstring(tree) is not None
    except Exception:
        return False

def fix_docstring(rel_path: str, src_dir: Path):
    path = src_dir / rel_path / "__init__.py"
    if not path.exists():
        print(f"Skipping {rel_path}: __init__.py not found at {path}")
        return

    if has_docstring(path):
        print(f"Skipping {rel_path}: Already has docstring")
        return

    docstring = DOCSTRINGS.get(rel_path, f'"""Module for {Path(rel_path).name}."""\n')
    
    print(f"Fixing {rel_path}")
    try:
        content = path.read_text()
        path.write_text(docstring + "\n" + content)
    except Exception as e:
        print(f"Error fixing {rel_path}: {e}", file=sys.stderr)

def main():
    parser = argparse.ArgumentParser(description="Fix missing docstrings in __init__.py files.")
    parser.add_argument("--root", type=Path, default=Path(__file__).parent.parent, help="Project root directory")
    parser.add_argument("--target", action="append", help="Specific target module (relative to src/codomyrmex). Can be used multiple times.")
    parser.add_argument("--all", action="store_true", help="Run on all default targets")
    
    args = parser.parse_args()
    
    root_dir = args.root
    src_dir = root_dir / "src" / "codomyrmex"
    
    if not src_dir.exists():
        print(f"Error: Source directory {src_dir} does not exist.")
        return

    targets = args.target if args.target else []
    if args.all or not targets:
         # If --all is specified, OR if no targets are specified (default behavior), use default targets?
         # Wait, if I want to just run --help and do nothing, I shouldn't run defaults by default unless explicit?
         # Current script runs defaults immediately. Let's keep that behavior but allow overriding.
         if not targets:
             targets = DEFAULT_TARGETS
    
    print(f"Fixing {len(targets)} modules...")
    for target in targets:
        fix_docstring(target, src_dir)
    print("Done.")

if __name__ == "__main__":
    main()
