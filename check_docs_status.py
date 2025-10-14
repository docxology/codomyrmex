#!/usr/bin/env python3
"""
Script to check documentation status across the entire repository.
Checks for README.md and AGENTS.md files in all directories.
"""

import os
import sys
from pathlib import Path

def check_documentation_status():
    """Check which directories are missing README.md and/or AGENTS.md files."""

    repo_root = Path("/Users/4d/Documents/GitHub/codomyrmex")

    # List of directories to check (excluding common ignore patterns)
    ignore_patterns = [
        "__pycache__",
        ".git",
        "node_modules",
        ".pytest_cache",
        "build",
        "dist",
        "*.egg-info"
    ]

    missing_readme = []
    missing_agents = []
    has_both = []
    has_readme_only = []
    has_agents_only = []

    # Walk through all directories in the repo, excluding common ignore patterns
    for dir_path in repo_root.rglob("*"):
        if dir_path.is_dir():
            rel_path = str(dir_path.relative_to(repo_root))

            # Skip directories that match ignore patterns or contain them
            if any(pattern in rel_path for pattern in ignore_patterns) or any(rel_path.startswith(pattern) for pattern in ignore_patterns):
                continue

            # Skip virtual environment and other external directories
            if any(skip in rel_path for skip in ['.venv/', 'node_modules/', '.git/', '__pycache__/']):
                continue

            readme_exists = (dir_path / "README.md").exists()
            agents_exists = (dir_path / "AGENTS.md").exists()

            if readme_exists and agents_exists:
                has_both.append(rel_path)
            elif readme_exists:
                has_readme_only.append(rel_path)
            elif agents_exists:
                has_agents_only.append(rel_path)
            else:
                missing_readme.append(rel_path)
                missing_agents.append(rel_path)

    return {
        'missing_readme': sorted(missing_readme),
        'missing_agents': sorted(missing_agents),
        'has_both': sorted(has_both),
        'has_readme_only': sorted(has_readme_only),
        'has_agents_only': sorted(has_agents_only)
    }

def print_report(results):
    """Print a formatted report of documentation status."""

    print("📋 REPOSITORY DOCUMENTATION STATUS REPORT")
    print("=" * 50)

    print(f"\n✅ Directories with both README.md and AGENTS.md: {len(results['has_both'])}")
    if results['has_both']:
        for dir_path in results['has_both'][:10]:  # Show first 10
            print(f"   • {dir_path}")
        if len(results['has_both']) > 10:
            print(f"   ... and {len(results['has_both']) - 10} more")

    print(f"\n📖 Directories with README.md only: {len(results['has_readme_only'])}")
    for dir_path in results['has_readme_only']:
        print(f"   • {dir_path}")

    print(f"\n🤖 Directories with AGENTS.md only: {len(results['has_agents_only'])}")
    for dir_path in results['has_agents_only']:
        print(f"   • {dir_path}")

    print(f"\n❌ Missing README.md: {len(results['missing_readme'])}")
    for dir_path in results['missing_readme']:
        print(f"   • {dir_path}")

    print(f"\n🚫 Missing AGENTS.md: {len(results['missing_agents'])}")
    for dir_path in results['missing_agents']:
        print(f"   • {dir_path}")

    total_dirs = len(results['has_both']) + len(results['has_readme_only']) + len(results['has_agents_only']) + len(results['missing_readme'])
    coverage = (len(results['has_both']) + len(results['has_readme_only']) + len(results['has_agents_only'])) / total_dirs * 100
    print(f"\n📊 Total directories checked: {total_dirs}")
    print(".2f")

if __name__ == "__main__":
    results = check_documentation_status()
    print_report(results)
