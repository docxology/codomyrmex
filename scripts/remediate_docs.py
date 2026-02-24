#!/usr/bin/env python3
"""
scripts/remediate_docs.py

Walks the project directory tree and creates missing documentation files
(README.md, SPEC.md, AGENTS.md) in every subdirectory that doesn't already
have them.  Uses only stdlib ``pathlib`` — no external tools required.

Usage:
    python remediate_docs.py [--root ROOT]

    --root  Project root directory (default: parent of the scripts/ directory)
"""

import argparse
from pathlib import Path

from codomyrmex.utils.cli_helpers import print_error, print_info, print_success

_EXCLUDE_DIRS = {".git", "__pycache__", ".venv", ".gemini", "tmp", "vendor"}
_EXCLUDE_PATTERNS = {"*.egg-info", ".pytest_cache", ".mypy_cache"}


def get_target_directories(root_dir: Path) -> list:
    """Return all subdirectories under *root_dir* suitable for doc generation.

    Excludes hidden/cache/vendor directories and their descendants.

    Args:
        root_dir: Project root to walk.

    Returns:
        Sorted list of ``Path`` objects for qualifying directories,
        with *root_dir* itself as the first entry.
    """
    results = [root_dir]
    for dirpath in sorted(root_dir.rglob("*")):
        if not dirpath.is_dir():
            continue
        # Skip if any path component is in the exclude set
        parts = dirpath.relative_to(root_dir).parts
        if any(p in _EXCLUDE_DIRS for p in parts):
            continue
        # Skip directories whose name matches an exclude pattern
        if any(dirpath.match(pat) for pat in _EXCLUDE_PATTERNS):
            continue
        results.append(dirpath)
    return results


def generate_docs(root_dir: Path) -> None:
    """Create missing README.md, SPEC.md, and AGENTS.md in qualifying directories.

    Args:
        root_dir: Project root directory.
    """
    target_dirs = get_target_directories(root_dir)
    missing_count = 0
    created_count = 0

    for dirpath in target_dirs:
        dir_name = dirpath.name if dirpath != root_dir else "Codomyrmex Root"

        readme_content = f"""# {dir_name}

## Overview
This directory contains the real, functional implementations and components for the `{dir_name}` module within the Codomyrmex ecosystem.

## Principles
- **Functional Integrity**: All methods and classes within this directory are designed to be fully operational and production-ready.
- **Zero-Mock Policy**: Code herein adheres to the strict Zero-Mock testing policy, ensuring all tests run against real logic.
"""

        spec_content = f"""# {dir_name} Specification

## Purpose
This specification formally defines the expected behavior, interfaces, and architecture for the `{dir_name}` module.

## Architectural Constraints
- **Modularity**: Components must maintain strict modular boundaries.
- **Real Execution**: The design guarantees executable paths without reliance on stubbed or mocked data.
- **Data Integrity**: All input and output signatures must be strictly validated.
"""

        agents_content = f"""# {dir_name} Agentic Context

## Agent Overview
This file provides context for autonomous agents operating within the `{dir_name}` module.

## Operational Directives
1. **Context Awareness**: Agents modifying or analyzing this directory must understand its role within the broader Codomyrmex system.
2. **Functional Enforcement**: Agents must ensure any generated code remains fully functional and real.
3. **Documentation Sync**: Agents must keep this `AGENTS.md`, `README.md`, and `SPEC.md` synchronized with actual code capabilities.
"""

        docs = {
            "README.md": readme_content,
            "SPEC.md": spec_content,
            "AGENTS.md": agents_content,
        }

        for doc_name, content in docs.items():
            doc_path = dirpath / doc_name
            if not doc_path.exists():
                missing_count += 1
                try:
                    doc_path.write_text(content, encoding="utf-8")
                    created_count += 1
                except Exception as e:
                    print_error(f"Error creating {doc_path}: {e}")

    print_info(f"Identified {missing_count} missing documentation files.")
    print_success(f"Successfully created {created_count} documentation files.")


def main() -> int:
    """Parse arguments and run documentation generation."""
    default_root = str(Path(__file__).resolve().parent.parent)
    parser = argparse.ArgumentParser(
        description="Create missing README/SPEC/AGENTS documentation in project directories."
    )
    parser.add_argument(
        "--root",
        default=default_root,
        help=f"Project root directory (default: {default_root})",
    )
    args = parser.parse_args()

    root_dir = Path(args.root).resolve()
    print_info(f"Starting documentation generation in {root_dir}...")
    generate_docs(root_dir)
    return 0


if __name__ == "__main__":
    main()
