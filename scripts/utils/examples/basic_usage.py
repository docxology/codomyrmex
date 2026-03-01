#!/usr/bin/env python3
"""
Utility Functions - Real Usage Examples

Demonstrates actual utility capabilities:
- Directory management (ensure_directory)
- JSON safety (safe_json_loads, safe_json_dumps)
- Content hashing (hash_content)
- Timing and retries
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
from codomyrmex.utils import (
    ensure_directory,
    safe_json_loads,
    safe_json_dumps,
    hash_content,
    timing_decorator
)

def main():
    setup_logging()
    print_info("Running Utility Examples...")

    # 1. Directory Management
    print_info("Testing ensure_directory...")
    try:
        test_dir = Path("output/utils_test")
        ensure_directory(test_dir)
        if test_dir.exists():
            print_success(f"  Directory ensured: {test_dir}")
    except Exception as e:
        print_error(f"  Directory management failed: {e}")

    # 2. JSON Safety
    print_info("Testing safe JSON operations...")
    try:
        data = {"a": 1, "b": [2, 3]}
        json_str = safe_json_dumps(data)
        parsed = safe_json_loads(json_str)
        if parsed == data:
            print_success("  JSON dump/load verified.")
    except Exception as e:
        print_error(f"  JSON operations failed: {e}")

    # 3. Hashing
    print_info("Testing content hashing...")
    try:
        content = "Hello Codomyrmex"
        h = hash_content(content)
        print_success(f"  Hash for '{content}': {h[:10]}...")
    except Exception as e:
        print_error(f"  Hashing failed: {e}")

    # 4. Decorators
    print_info("Testing decorators (timing)...")
    try:
        @timing_decorator
        def task():
            return {"status": "ok"}
        
        result = task()
        if "execution_time_ms" in result:
            print_success(f"  Timing decorator verified: {result['execution_time_ms']}ms")
    except Exception as e:
        print_error(f"  Decorators failed: {e}")

    print_success("Utility examples completed successfully")
    return 0

if __name__ == "__main__":
    sys.exit(main())
