# Agent Guidelines - Performance

**Version**: v1.1.4 | **Status**: Active | **Last Updated**: March 2026

## Module Overview

Lazy loading, caching, profiling, and performance monitoring. Provides `LazyLoader` for deferred
module imports, `CacheManager` for TTL-based in-memory caching, `AsyncProfiler` for async code
profiling, and two MCP tools (`performance_check_regression`, `performance_compare_benchmarks`)
for benchmark regression detection and comparison.

## Key Files

| File | Purpose |
|------|---------|
| `__init__.py` | Exports `LazyLoader`, `CacheManager`, `PerformanceMonitor`, `AsyncProfiler`, `ResourceTracker`, `lazy_import`, `cached_function`, `monitor_performance` |
| `lazy_loader.py` | `LazyLoader`, `lazy_import()` — defer module loading until first use |
| `cache_manager.py` | `CacheManager` — cache with TTL and multiple backends |
| `performance_monitor.py` | `PerformanceMonitor` — system metrics (requires psutil) |
| `async_profiler.py` | `AsyncProfiler` — profile async code execution |
| `resource_tracker.py` | `ResourceTracker` — track memory and CPU usage |
| `mcp_tools.py` | MCP tools: `performance_check_regression`, `performance_compare_benchmarks` |

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

| Tool | Description | Trust Level |
|------|-------------|-------------|
| `performance_check_regression` | Check a benchmark result against a stored baseline for regressions | SAFE |
| `performance_compare_benchmarks` | Compute the delta between two benchmark values | SAFE |

## Operating Contracts

- `AsyncProfiler` must be instantiated (`profiler = AsyncProfiler()`) before using `@profiler.profile`; do NOT use `@AsyncProfiler.profile` (class-level) — this causes runtime errors
- `CacheManager.set()` with `ttl=None` stores indefinitely — always set TTL in production
- `PerformanceMonitor` requires `psutil` — will raise `ImportError` if not installed
- `performance_check_regression` is read-only — does not modify baseline files
- **DO NOT** call `@AsyncProfiler.profile` as a class decorator — always use an instance

## PAI Agent Role Access Matrix

| PAI Agent | Access Level | MCP Tools | Trust Level |
|-----------|-------------|-----------|-------------|
| **Engineer** | Full | `performance_check_regression`, `performance_compare_benchmarks` | TRUSTED |
| **Architect** | Read + Design | `performance_compare_benchmarks` — baseline design, SLO specification | OBSERVED |
| **QATester** | Validation | `performance_check_regression`, `performance_compare_benchmarks` — regression detection, SLO verification | OBSERVED |
| **Researcher** | Read-only | `performance_compare_benchmarks`, `performance_check_regression` — benchmark analysis | SAFE |

### Engineer Agent
**Use Cases**: Running benchmarks during VERIFY, detecting performance regressions after BUILD, comparing baseline vs. current performance.

### Architect Agent
**Use Cases**: Setting performance baselines, defining SLOs, reviewing benchmark configurations.

### QATester Agent
**Use Cases**: Detecting performance regressions during VERIFY, confirming benchmarks meet SLO targets.

### Researcher Agent
**Use Cases**: Analyzing benchmark deltas and regression signals during research and performance studies.

## Navigation

- [README](README.md) | [SPEC](SPEC.md) | [PAI](PAI.md)


## Rule Reference

This module is governed by the following rule file:

- [`src/codomyrmex/agentic_memory/rules/modules/performance.cursorrules`](src/codomyrmex/agentic_memory/rules/modules/performance.cursorrules)
