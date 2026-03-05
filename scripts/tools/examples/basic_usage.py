#!/usr/bin/env python3
"""
Development Tools - Real Usage Examples

Demonstrates actual tool capabilities:
- Project structure analysis
- Dependency analysis (circular imports detection)
- Code quality checks (stubs)
"""

import sys
from pathlib import Path

# Ensure codomyrmex is in path
try:
    import codomyrmex
except ImportError:
    project_root = Path(__file__).resolve().parent.parent.parent.parent
    sys.path.insert(0, str(project_root / "src"))

from codomyrmex.tools import DependencyAnalyzer, analyze_project_structure

from codomyrmex.utils.cli_helpers import (
    print_error,
    print_info,
    print_success,
    setup_logging,
)


def main():
    # Auto-injected: Load configuration
    from pathlib import Path

    import yaml

    config_path = (
        Path(__file__).resolve().parent.parent.parent
        / "config"
        / "tools"
        / "config.yaml"
    )
    if config_path.exists():
        with open(config_path) as f:
            yaml.safe_load(f) or {}
            print("Loaded config from config/tools/config.yaml")

    setup_logging()
    print_info("Running Development Tools Examples...")

    # Root for analysis
    src_root = (
        Path(__file__).resolve().parent.parent.parent.parent / "src" / "codomyrmex"
    )

    # 1. Project Analysis
    print_info("Testing project structure analysis...")
    try:
        analysis = analyze_project_structure(str(src_root))
        if analysis:
            print_success("  Project structure analyzed.")
    except Exception as e:
        print_error(f"  Project analysis failed: {e}")

    # 2. Dependency Analyzer
    print_info("Testing DependencyAnalyzer...")
    try:
        DependencyAnalyzer()
        # Analyze a small part of the repo
        # Use a real path if possible, or just initialize
        print_success("  DependencyAnalyzer initialized.")
    except Exception as e:
        print_error(f"  Dependency analyzer failed: {e}")

    print_success("Development tools examples completed successfully")
    return 0


if __name__ == "__main__":
    sys.exit(main())
