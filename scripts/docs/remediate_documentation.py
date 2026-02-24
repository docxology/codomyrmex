#!/usr/bin/env python3
"""
scripts/remediate_documentation.py

Remediates documentation gaps:
1. Creates 'py.typed' in all package directories.
2. Generates missing RASP files (README, AGENTS, SPEC, PAI) with template content.
"""

import os
import argparse
from pathlib import Path
from typing import List

REQUIRED_DOCS = ["README.md", "AGENTS.md", "SPEC.md", "PAI.md"]

TEMPLATES = {
    "README.md": """# {name}

## Overview

{docstring}

**Status**: Active
**,Last Updated**: February 2026
""",

    "AGENTS.md": """# {name} Agents

**Status**: Active
**Last Updated**: February 2026

## Purpose

{docstring}

## Components

- `__init__.py`: Module entry point
""",

    "SPEC.md": """# {name} Specification

**Status**: Active
**Last Updated**: February 2026

## Functional Requirements

1. Provide {name} functionality.
2. Integrate with codomyrmex ecosystem.

## API Contract

- Follows standard codomyrmex module structure.
""",

    "PAI.md": """# {name} Personal AI Infrastructure

**Status**: Active
**Last Updated**: February 2026

## AI Capabilities

- Provides context and tools for {name}
"""
}

def get_docstring_summary(path: Path) -> str:
    init_file = path / "__init__.py"
    if init_file.exists():
        try:
            content = init_file.read_text()
            # Simple extraction of first docstring line if exists
            if '"""' in content:
                parts = content.split('"""')
                if len(parts) >= 3:
                    return parts[1].strip().split('\n')[0]
            if "'''" in content:
                parts = content.split("'''")
                if len(parts) >= 3:
                    return parts[1].strip().split('\n')[0]
        except Exception:
            pass
    return f"Module for {path.name}"

def is_package(path: Path) -> bool:
    return path.is_dir() and (path / "__init__.py").exists()

def remediate_module(path: Path, src_dir: Path):
    print(f"Checking {path.relative_to(src_dir)}")
    
    # 1. Ensure py.typed
    py_typed = path / "py.typed"
    if not py_typed.exists():
        print(f"  + Creating py.typed in {path.name}")
        py_typed.touch()

    # 2. Ensure RASP files
    name = path.name.replace("_", " ").title()
    summary = get_docstring_summary(path)
    
    for doc_name, template in TEMPLATES.items():
        doc_path = path / doc_name
        if not doc_path.exists():
            print(f"  + Creating {doc_name} in {path.name}")
            content = template.format(name=name, docstring=summary)
            doc_path.write_text(content)

def main():
    parser = argparse.ArgumentParser(description="Remediate documentation gaps.")
    parser.add_argument("--root", type=Path, default=Path(__file__).parent.parent, help="Project root directory")
    args = parser.parse_args()

    root_dir = args.root
    src_dir = root_dir / "src" / "codomyrmex"
    
    if not src_dir.exists():
        print(f"Error: Source directory {src_dir} does not exist.")
        return

    count = 0
    for root, dirs, files in os.walk(src_dir):
        root_path = Path(root)
        
        # Skip hidden directories
        if any(part.startswith('.') for part in root_path.relative_to(src_dir).parts):
            continue

        if is_package(root_path):
            remediate_module(root_path, src_dir)
            count += 1
            
    print(f"\nRemediation complete. Processed {count} modules.")

if __name__ == "__main__":
    main()
