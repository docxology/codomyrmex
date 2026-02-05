# performance

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

Performance optimization module providing lazy loading, function caching, and system monitoring for the Codomyrmex platform. The `LazyLoader` defers module imports until first access to reduce startup time, `CacheManager` stores expensive computation results with configurable TTL and eviction, and the optional `PerformanceMonitor` (requires `psutil`) provides real-time CPU, memory, and disk metrics along with function profiling decorators.

## Key Exports

### Core (always available)
- **`LazyLoader`** -- Proxy object that defers module import until an attribute is first accessed, reducing startup time
- **`lazy_import()`** -- Convenience function that returns a `LazyLoader` for a given module name
- **`CacheManager`** -- In-memory and file-backed cache with TTL expiration, max-size eviction, and JSON/pickle serialization
- **`cached_function()`** -- Decorator that caches function return values based on argument hashing

### Monitoring (optional, requires `psutil`)
- **`PerformanceMonitor`** -- Collects system metrics (CPU, memory, disk, network) and tracks function execution times
- **`monitor_performance()`** -- Decorator that instruments a function with timing and resource tracking
- **`performance_context()`** -- Context manager for measuring resource usage within a code block
- **`profile_function()`** -- Profiles a function call and returns detailed timing breakdown
- **`get_system_metrics()`** -- Returns a snapshot of current system resource usage

Note: When `psutil` is not installed, `monitor_performance`, `performance_context`, `profile_function`, and `get_system_metrics` are exported as no-op stubs that pass through without effect.

## Directory Contents

- `lazy_loader.py` -- LazyLoader class and lazy_import convenience function for deferred imports
- `cache_manager.py` -- CacheManager with TTL, eviction policies, and the cached_function decorator
- `performance_monitor.py` -- PerformanceMonitor, system metrics collection, and profiling (requires psutil)
- `async_profiler.py` -- Async-compatible profiling utilities for coroutine performance measurement
- `resource_tracker.py` -- Resource usage tracking and reporting over time
- `requirements.txt` -- Optional dependencies (psutil) for monitoring features

## Navigation

- **Full Documentation**: [docs/modules/performance/](../../../docs/modules/performance/)
- **Parent Directory**: [codomyrmex](../README.md)
- **Project Root**: ../../../README.md
