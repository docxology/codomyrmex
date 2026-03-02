# Performance Profiling - Technical Specification

**Module**: `codomyrmex.performance.profiling`
**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Architecture

Two profiling approaches: `AsyncProfiler` for decorator-based per-function timing with slow-call detection, and `BenchmarkSuite` / `run_benchmark` for multi-iteration comparative benchmarking.

## Key Classes

### AsyncProfiler

| Method | Signature | Description |
|--------|-----------|-------------|
| `profile` | `(func: Callable) -> Callable` | Async function decorator measuring duration with `time.perf_counter` |
| `profile_sync` | `(func: Callable) -> Callable` | Sync function decorator with same measurements |
| `record` | `(function_name, duration, error?)` | Manual profiling entry |
| `get_stats` | `(function_name) -> ProfileStats \| None` | Aggregate stats for a function |
| `all_stats` | `() -> list[ProfileStats]` | Stats for all profiled functions |
| `summary` | `() -> dict` | Overview: function count, total calls, slow calls, per-function avg/max ms |
| `clear` | `()` | Reset all profiling data |

Constructor: `AsyncProfiler(slow_threshold: float = 1.0)` -- seconds.

### BenchmarkSuite

| Method | Signature | Description |
|--------|-----------|-------------|
| `add` | `(result: BenchmarkResult)` | Add a benchmark result to the suite |
| `report` | `() -> str` | Tabular report of all results |
| `compare` | `(name_a, name_b) -> dict` | Side-by-side comparison with speedup ratio |

### Key Functions

| Function | Signature | Description |
|----------|-----------|-------------|
| `run_benchmark` | `(func, iterations=100, warmup=3, **kwargs) -> BenchmarkResult` | Time a function over N iterations |
| `compare_benchmarks` | `(func_a, func_b, iterations=100) -> dict` | Compare two functions head-to-head |
| `profile_function` | `(func, *args, **kwargs) -> dict` | Single-run timing + optional memory delta |

### ProfileStats (dataclass)

Fields: `function_name`, `call_count`, `total_seconds`, `min_seconds`, `max_seconds`, `error_count`. Properties: `avg_seconds`, `avg_ms`, `max_ms`.

### BenchmarkResult (dataclass)

Fields: `name`, `timings` (list of floats), `iterations`. Properties: `mean`, `std_dev`, `min_time`, `max_time`, `p50`, `p75`, `p90`, `p95`, `p99`.

## Dependencies

- `time.perf_counter`: High-resolution timer for all measurements.
- `gc` / `tracemalloc`: Optional memory tracking in `profile_function`.
- No external dependencies.

## Constraints

- `AsyncProfiler` must be instantiated before use as a decorator; class-level decoration will fail.
- Profiling entries are stored in unbounded lists; call `clear()` to release memory.
- `run_benchmark` warmup iterations are excluded from `BenchmarkResult.timings`.
- Slow calls (exceeding `slow_threshold`) are logged at WARNING via the module logger.

## Error Handling

- Profiled functions that raise exceptions still record duration and error message in `ProfileEntry`.
- `get_stats()` returns `None` for functions with no recorded entries.
