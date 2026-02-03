#!/usr/bin/env python3
"""
scripts/fix_missing_docstrings.py

Prepends docstrings to __init__.py files that are missing them.
Targeted at a specific list of modules identified in the audit.
"""

from pathlib import Path
import ast

ROOT_DIR = Path(__file__).parent.parent
SRC_DIR = ROOT_DIR / "src" / "codomyrmex"

# List of relative paths to packages that are missing docstrings
TARGETS = [
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

def fix_docstring(rel_path: str):
    path = SRC_DIR / rel_path / "__init__.py"
    if not path.exists():
        print(f"Skipping {rel_path}: __init__.py not found")
        # specific handling for tests/unit/tools if it's actually tests/unit/tools/__init__.py
        return

    if has_docstring(path):
        print(f"Skipping {rel_path}: Already has docstring")
        return

    docstring = DOCSTRINGS.get(rel_path, f'"""Module for {Path(rel_path).name}."""\n')
    
    print(f"Fixing {rel_path}")
    content = path.read_text()
    path.write_text(docstring + "\n" + content)

def main():
    print(f"Fixing {len(TARGETS)} modules...")
    for target in TARGETS:
        fix_docstring(target)
    print("Done.")

if __name__ == "__main__":
    main()
