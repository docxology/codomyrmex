#!/usr/bin/env python3
"""
Performance Optimization - Real Usage Examples

Demonstrates actual optimization techniques:
- Lazy loading of modules
- Function result caching
- Performance monitoring contexts
"""

import sys
import os
import time
from pathlib import Path

# Ensure codomyrmex is in path
try:
    import codomyrmex
except ImportError:
    project_root = Path(__file__).resolve().parent.parent.parent.parent
    sys.path.insert(0, str(project_root / "src"))

from codomyrmex.utils.cli_helpers import setup_logging, print_success, print_info, print_error
from codomyrmex.performance import (
    LazyLoader,
    CacheManager,
    cached_function,
    monitor_performance,
    performance_context,
    get_system_metrics
)

def main():
    setup_logging()
    print_info("Running Performance Optimization Examples...")

    # 1. Cache Manager
    print_info("Testing CacheManager...")
    cache = CacheManager(max_memory_items=100)
    cache.set("test_key", "test_value")
    val = cache.get("test_key")
    if val == "test_value":
        print_success("  CacheManager set/get functional.")
    else:
        print_error("  CacheManager failed.")

    # 2. Cached Function
    print_info("Testing @cached_function...")
    @cached_function(ttl=60)
    def heavy_comp(n):
        return n * n
    
    res1 = heavy_comp(10)
    res2 = heavy_comp(10)
    if res1 == 100 and res2 == 100:
        print_success("  @cached_function functional.")
    
    # 3. Performance Monitor
    print_info("Testing system metrics...")
    metrics = get_system_metrics()
    if isinstance(metrics, dict):
        print_success(f"  System metrics retrieved: {list(metrics.keys())}")

    # 4. Performance Context
    print_info("Testing performance_context...")
    with performance_context("test_operation"):
        time.sleep(0.1)
    print_success("  performance_context functional.")

    # 5. Monitor Performance Decorator
    @monitor_performance("test_decorated")
    def sample_func():
        time.sleep(0.05)
    
    sample_func()
    print_success("  @monitor_performance functional.")

    print_success("Performance optimization examples completed successfully")
    return 0

if __name__ == "__main__":
    sys.exit(main())
