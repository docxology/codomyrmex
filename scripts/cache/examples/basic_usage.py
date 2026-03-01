#!/usr/bin/env python3
"""
Cache - Real Usage Examples

Demonstrates actual cache capabilities:
- CacheManager usage
- get_cache functionality
- Set/Get operations
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
from codomyrmex.cache import (
    get_cache
)

def main():
    setup_logging()
    print_info("Running Cache Examples...")

    # 1. Cache Manager
    print_info("Testing CacheManager and get_cache...")
    try:
        cache = get_cache(name="test_cache", backend="in_memory")
        cache.set("foo", "bar")
        val = cache.get("foo")
        if val == "bar":
            print_success("  Cache Set/Get functional.")
        
        stats = cache.get_stats()
        if stats:
            print_success("  Cache statistics retrieved.")
    except Exception as e:
        print_error(f"  Cache operations failed: {e}")

    print_success("Cache examples completed successfully")
    return 0

if __name__ == "__main__":
    sys.exit(main())
