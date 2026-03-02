#!/usr/bin/env python3
"""
Basic coding Usage

Demonstrates basic usage patterns.
"""

import sys
from pathlib import Path

# Ensure codomyrmex is in path
try:
    import codomyrmex  # noqa: F401
except ImportError:
    project_root = Path(__file__).resolve().parent.parent.parent.parent
    sys.path.insert(0, str(project_root / "src"))

from codomyrmex.utils.cli_helpers import setup_logging, print_success, print_info

def main():
    setup_logging()
    print_info(f"Running Basic coding Usage...")

    # 1. Code Execution
    print_info("Testing code execution...")
    try:
        from codomyrmex.coding import execute_code, SUPPORTED_LANGUAGES
        code = "print('Hello from Codomyrmex!')"
        # Correct order: language, code
        result = execute_code("python", code)
        if result.get("success") or result.get("exit_code") == 0:
            print_success(f"  Execution result: {result.get('stdout', '').strip()}")
        else:
            print_info(f"  Execution result note: {result.get('stderr', '').strip()}")
        print_success(f"  Supported languages count: {len(SUPPORTED_LANGUAGES)}")
    except Exception as e:
        print_info(f"  Code execution note: {e}")

    # 2. Code Review / Analysis
    print_info("Testing code analysis...")
    try:
        from codomyrmex.coding import analyze_file
        # Analyze this script itself
        report = analyze_file(__file__)
        if report:
            print_success(f"  Analysis completed for {Path(__file__).name}")
    except Exception as e:
        print_info(f"  Code analysis demo note: {e}")

    # 3. Sandbox / Monitoring (Interface Check)
    print_info("Checking Sandbox and Monitor interfaces...")
    try:
        from codomyrmex.coding import ExecutionMonitor, check_docker_available
        monitor = ExecutionMonitor()
        docker = check_docker_available()
        print_success(f"  ExecutionMonitor initialized. Docker available: {docker}")
    except Exception as e:
        print_info(f"  Sandbox/Monitor demo: {e}")

    print_success(f"Coding Usage completed successfully")
    return 0

if __name__ == "__main__":
    sys.exit(main())
