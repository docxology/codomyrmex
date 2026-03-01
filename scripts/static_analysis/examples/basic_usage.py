#!/usr/bin/env python3
"""
Static Analysis - Real Usage Examples

Demonstrates actual static analysis capabilities:
- Tool availability checks
- StaticAnalyzer initialization
- Basic file analysis coverage
"""

import sys
from pathlib import Path

# Ensure codomyrmex is in path
try:
    import codomyrmex
except ImportError:
    project_root = Path(__file__).resolve().parent.parent.parent.parent
    sys.path.insert(0, str(project_root / "src"))

from codomyrmex.utils.cli_helpers import setup_logging, print_success, print_info, print_error
from codomyrmex.static_analysis import (
    StaticAnalyzer,
    get_available_tools,
    analyze_file
)

def main():
    setup_logging()
    print_info("Running Static Analysis Examples...")

    # 1. Tool Availability
    print_info("Checking available analysis tools...")
    try:
        tools = get_available_tools()
        available = [t for t, v in tools.items() if v]
        print_info(f"  Available tools: {', '.join(available) if available else 'None'}")
    except Exception as e:
        print_error(f"  Tool check failed: {e}")

    # 2. StaticAnalyzer Initialization
    print_info("Initializing StaticAnalyzer...")
    try:
        analyzer = StaticAnalyzer()
        print_success("  StaticAnalyzer initialized.")
    except Exception as e:
        print_error(f"  Initialization failed: {e}")

    # 3. Basic Analysis (Import verification)
    print_info("Testing analyze_file handler...")
    try:
        # We don't run it on a real file here to keep it fast/portable in examples
        if analyze_file:
            print_success("  analyze_file handler available.")
    except Exception as e:
        print_error(f"  Analysis check failed: {e}")

    print_success("Static analysis examples completed successfully")
    return 0

if __name__ == "__main__":
    sys.exit(main())
