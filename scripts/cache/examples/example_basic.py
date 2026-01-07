#!/usr/bin/env python3
"""
Example: Cache System - Caching Functionality

This example demonstrates the Codomyrmex caching system.

CORE FUNCTIONALITY:
- Cache management
- Backend selection
- TTL configuration
- Cache statistics

USAGE EXAMPLES:
    # Basic caching
    from codomyrmex.cache import CacheManager, get_cache
    cache = get_cache()
    cache.set("key", "value", ttl=3600)
    value = cache.get("key")
"""
import sys
from pathlib import Path

# Add src to path for importing Codomyrmex modules
current_dir = Path(__file__).parent
project_root = current_dir.parent.parent
sys.path.insert(0, str(project_root / "src"))

# Import common utilities
sys.path.insert(0, str(project_root / "examples" / "_common"))
from config_loader import load_config
from example_runner import ExampleRunner
from utils import print_section, print_results, print_success, print_error

from codomyrmex.cache import CacheManager, get_cache

def main():
    """Run the cache system example."""
    print_section("Cache System Example")
    print("Demonstrating caching functionality")

    try:
        config = load_config(Path(__file__).parent / "config.yaml")
        print_success("Configuration loaded successfully")
    except Exception as e:
        print_error(f"Failed to load configuration: {e}")
        config = {}

    runner = ExampleRunner(__file__, config)
    runner.start()

    try:
        # Initialize cache manager
        cache_manager = CacheManager()
        print_success("✓ Cache manager initialized")

        # Get cache instance
        cache = get_cache()
        print_success("✓ Cache instance obtained")

        operations_summary = {
            "cache_manager_initialized": True,
            "cache_instance_obtained": True
        }

        print_results(operations_summary, "Operations Summary")
        runner.validate_results(operations_summary)
        runner.save_results(operations_summary)
        runner.complete()

        print("\n✅ Cache System example completed successfully!")
    except Exception as e:
        runner.error("Cache System example failed", e)
        sys.exit(1)

if __name__ == "__main__":
    main()

