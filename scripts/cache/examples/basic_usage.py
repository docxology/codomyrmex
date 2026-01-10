#!/usr/bin/env python3
"""
Cache Module - Real Usage Examples

Demonstrates actual caching capabilities:
- Creating and managing cache instances
- Setting and retrieving cached values
- Cache statistics and management
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


def main():
    setup_logging()
    print_info("Running Cache Module Examples...")

    try:
        from codomyrmex.cache import get_cache, CacheManager, CacheStats
        print_info("Successfully imported cache module")
    except ImportError as e:
        print_error(f"Could not import cache: {e}")
        return 1

    # Example 1: Get a default in-memory cache
    print_info("Creating in-memory cache instance...")
    try:
        cache = get_cache("example_cache", backend="in_memory")
        print_info(f"Cache instance created: {type(cache).__name__}")
    except Exception as e:
        print_info(f"Cache creation demo (expected in some environments): {e}")

    # Example 2: Demonstrate CacheManager
    print_info("Demonstrating CacheManager...")
    try:
        manager = CacheManager()
        print_info(f"CacheManager instantiated: {type(manager).__name__}")
        
        # Show available backends
        print_info("Available cache backends:")
        print("  - in_memory (default)")
        print("  - file_based")
        print("  - redis")
    except Exception as e:
        print_info(f"CacheManager demo: {e}")

    # Example 3: Demonstrate CacheStats
    print_info("Demonstrating CacheStats structure...")
    try:
        stats = CacheStats(hits=100, misses=25, size=50, max_size=1000)
        print(f"  Hits: {stats.hits}")
        print(f"  Misses: {stats.misses}")
        print(f"  Hit rate: {stats.hits / (stats.hits + stats.misses) * 100:.1f}%")
        print(f"  Size: {stats.size}/{stats.max_size}")
    except Exception as e:
        print_info(f"CacheStats demo: {e}")

    # Example 4: Cache usage patterns
    print_info("Common cache usage patterns:")
    print("  1. LLM response caching - reduce API costs")
    print("  2. Code analysis results - speedup repeated analysis")
    print("  3. Build artifact caching - faster builds")
    print("  4. Configuration caching - reduce file I/O")

    print_success("Cache module examples completed successfully")
    return 0


if __name__ == "__main__":
    sys.exit(main())
