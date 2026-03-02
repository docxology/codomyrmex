# Performance Profiling - Agentic Context

**Module**: `codomyrmex.performance.profiling`
**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Key Components

| Component | Purpose | Key Methods |
|-----------|---------|-------------|
| `AsyncProfiler` | Decorator-based profiler for async and sync functions with slow-call threshold alerts | `profile()` (async), `profile_sync()`, `record()`, `get_stats()`, `all_stats()`, `summary()` |
| `ProfileEntry` | Single measurement: function name, duration, timestamp, error | Dataclass |
| `ProfileStats` | Aggregate stats: call count, total/min/max seconds, error count | Properties: `avg_seconds`, `avg_ms`, `max_ms` |
| `BenchmarkSuite` | Named collection of benchmark results with tabular reporting | `add()`, `report()`, `compare()` |
| `run_benchmark()` | Run a function N iterations with warmup, returning `BenchmarkResult` | Standalone function |
| `compare_benchmarks()` | Side-by-side comparison of two functions with speedup ratio | Returns comparison dict |
| `PerformanceProfiler` | Class wrapper combining `time.perf_counter` timing with optional memory delta tracking | `run()`, `report()` |

## Operating Contracts

- `AsyncProfiler` must be instantiated before decorating: `profiler = AsyncProfiler(); @profiler.profile`. Class-level `@AsyncProfiler.profile` will fail.
- Slow-call threshold defaults to 1.0 second; calls exceeding it are logged at WARNING level and appended to `_slow_calls`.
- `run_benchmark()` supports a `warmup` parameter (default 3) to exclude cold-start iterations from results.
- `BenchmarkResult` computes percentiles (p50, p75, p90, p95, p99) from raw timings.

## Integration Points

- **time.perf_counter**: High-resolution timer used for all duration measurements.
- **gc/tracemalloc**: Optional memory tracking in `profile_function()` for memory delta reporting.
- **performance/monitoring**: Complements `ResourceTracker` -- profiling measures function-level latency while monitoring tracks system-level resources.

## Constraints

- `AsyncProfiler.profile` wraps async functions only; use `profile_sync` for synchronous functions.
- Profiling data is stored in memory with no size limit; call `clear()` to release when no longer needed.
