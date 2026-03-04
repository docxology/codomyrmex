# Performance Benchmarking -- Technical Specification

**Version**: v1.1.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

Two-component benchmarking toolkit: `BenchmarkRunner` for executing timed iterations
of callable functions with pass/fail certification against thresholds, and
`benchmark_comparison` for computing statistical deltas between benchmark runs.

## Architecture

Both components are standalone with no external dependencies beyond stdlib.
`BenchmarkRunner` uses `time.monotonic()` for high-resolution wall-clock timing.
Statistical functions use standard formulas (sample stddev with Bessel's correction).

## Key Classes

### `BenchmarkRunner`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `add(name, fn, iterations, threshold_ms)` | `str, Callable, int=100, float=0.0` | `None` | Register a benchmark; threshold 0 = no limit |
| `run()` | -- | `BenchmarkSuite` | Execute all benchmarks sequentially |
| `to_markdown(suite)` | `BenchmarkSuite` | `str` | Render results as markdown table |
| `benchmark_count` | property | `int` | Number of registered benchmarks |

### `BenchmarkResult`

| Attribute | Type | Description |
|-----------|------|-------------|
| `name` | `str` | Benchmark identifier |
| `iterations` | `int` | Number of iterations executed |
| `total_ms` | `float` | Total elapsed time |
| `mean_ms` | `float` | Mean time per iteration |
| `min_ms` | `float` | Fastest iteration |
| `max_ms` | `float` | Slowest iteration |
| `ops_per_sec` | `float` | Operations per second (1000 / mean_ms) |
| `passed` | `bool` | True if mean_ms <= threshold_ms or threshold is 0 |
| `threshold_ms` | `float` | Maximum allowed mean time |

### `BenchmarkSuite`

| Attribute | Type | Description |
|-----------|------|-------------|
| `name` | `str` | Suite name (default: "Performance Suite") |
| `results` | `list[BenchmarkResult]` | Individual benchmark results |
| `total_ms` | `float` | Total suite execution time |
| `all_passed` | `bool` | True only if every benchmark passed |

### Statistical Functions

| Function | Parameters | Returns | Description |
|----------|-----------|---------|-------------|
| `compute_delta(name, before, after, higher_is_better)` | `str, float, float, bool=False` | `BenchmarkDelta` | Absolute + relative delta with improvement flag |
| `mean(values)` | `list[float]` | `float` | Arithmetic mean; 0.0 for empty list |
| `stddev(values)` | `list[float]` | `float` | Sample stddev (n-1); 0.0 for fewer than 2 values |
| `coefficient_of_variation(values)` | `list[float]` | `float` | CV as percentage; 0.0 if mean is zero |

## Dependencies

- **Internal**: None (standalone benchmarking utilities)
- **External**: stdlib only -- `time`, `math`, `dataclasses`, `collections.abc`

## Constraints

- `run()` executes benchmarks sequentially in registration order; no parallelism.
- Timing uses `time.monotonic()` (wall-clock, not CPU time); results include GC pauses and OS scheduling.
- `ops_per_sec` is computed as `1000 / mean_ms`; returns 0 if mean is 0.
- `compute_delta()` divides by `before`; returns `relative_delta=0.0` when `before` is 0.
- Zero-mock: all timings are real measurements; no simulated benchmarks in production code.

## Error Handling

- No exceptions raised by benchmark execution; failed thresholds set `passed=False`.
- `mean()` and `stddev()` handle empty inputs gracefully (return 0.0).
- Benchmark functions that raise exceptions will propagate up through `run()`.
