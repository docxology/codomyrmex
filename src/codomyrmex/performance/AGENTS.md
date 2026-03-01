# Agent Guidelines - Performance

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

## Module Overview

Lazy loading, caching, profiling, and performance monitoring.

## Key Classes

- **LazyLoader** — Defer module loading until first use
- **CacheManager** — Cache with TTL and multiple backends
- **PerformanceMonitor** — System metrics (requires psutil)
- **AsyncProfiler** — Profile async code execution
- **ResourceTracker** — Track memory and CPU usage

## Agent Instructions

1. **Lazy load heavy modules** — Use `lazy_import()` for numpy, pandas, etc.
2. **Cache expensive operations** — Use `@cached_function` decorator
3. **Profile hot paths** — Use `@monitor_performance` on performance-critical code
4. **Set appropriate TTL** — Cache TTL should match data freshness requirements
5. **Track resources in long-running code** — Use `ResourceTracker` for memory leaks

## Patterns

```python
from codomyrmex.performance import (
    lazy_import, cached_function, CacheManager, monitor_performance
)

# Lazy import heavy modules
np = lazy_import("numpy")
pd = lazy_import("pandas")

# Cache expensive functions
cache = CacheManager(ttl=300)

@cached_function(cache, key_fn=lambda x: f"result_{x}")
def expensive_computation(x):
    return x ** 2

# Profile functions
@monitor_performance(name="process_batch")
async def process_batch(items):
    for item in items:
        await process(item)
```

## Testing Patterns

```python
# Verify lazy loading works
np = lazy_import("numpy")
assert not hasattr(np, "_loaded")  # Not loaded yet
_ = np.array([1, 2, 3])  # Now loaded

# Verify caching
cache = CacheManager()
cache.set("key", "value", ttl=60)
assert cache.get("key") == "value"
```

## MCP Tools Available

All tools are auto-discovered via `@mcp_tool` decorators and exposed through the MCP bridge.

| Tool | Description | Trust Level |
|------|-------------|-------------|
| `performance_check_regression` | Check a benchmark result against a stored baseline for regressions | Safe |
| `performance_compare_benchmarks` | Compute the delta between two benchmark values | Safe |

## Navigation

- [README](README.md) | [SPEC](SPEC.md) | [PAI](PAI.md)
