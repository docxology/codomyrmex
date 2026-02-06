# Performance Module

**Version**: v0.1.0 | **Status**: Active

Lazy loading, caching, and performance monitoring utilities.

## Quick Start

```python
from codomyrmex.performance import (
    LazyLoader, lazy_import, CacheManager, cached_function
)

# Lazy import heavy modules
numpy = lazy_import("numpy")  # Only loads when first accessed
pandas = lazy_import("pandas")

# Caching
cache = CacheManager(backend="memory", ttl=300)

@cached_function(cache, ttl=60)
def expensive_computation(x):
    return x ** 2

result = expensive_computation(5)  # Computed
result = expensive_computation(5)  # Cached

# Manual cache operations
cache.set("key", {"data": 123})
value = cache.get("key")
cache.delete("key")
```

## Performance Monitoring

```python
from codomyrmex.performance import (
    PerformanceMonitor, monitor_performance, performance_context
)

# Decorator-based monitoring
@monitor_performance(name="process_data")
def process_data():
    # ... processing ...
    pass

# Context manager
with performance_context("batch_job") as ctx:
    run_batch()
    print(f"Duration: {ctx.duration}s, Memory: {ctx.memory_delta}MB")

# System metrics
monitor = PerformanceMonitor()
metrics = monitor.get_system_metrics()
print(f"CPU: {metrics['cpu_percent']}%, Memory: {metrics['memory_percent']}%")
```

## Exports

| Class/Function | Description |
|----------------|-------------|
| `LazyLoader` | Defer module loading |
| `lazy_import(name)` | Lazy import a module |
| `CacheManager` | Cache with TTL and backends |
| `cached_function` | Decorator for function caching |
| `PerformanceMonitor` | System metrics (requires psutil) |
| `monitor_performance` | Decorator for timing |
| `performance_context` | Context manager for profiling |

## Navigation

- [SPEC](SPEC.md) | [AGENTS](AGENTS.md) | [PAI](PAI.md)
