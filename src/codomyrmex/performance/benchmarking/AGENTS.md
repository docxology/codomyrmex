# Codomyrmex Agents -- src/codomyrmex/performance/benchmarking

**Version**: v1.0.8 | **Status**: Active | **Last Updated**: March 2026

## Purpose

Benchmark execution engine and statistical comparison utilities. `BenchmarkRunner`
runs timed iterations of callables with threshold certification. `benchmark_comparison`
provides delta computation, mean, standard deviation, and coefficient of variation
for comparing results across runs.

## Key Components

| File | Class / Function | Role |
|------|-----------------|------|
| `benchmark_runner.py` | `BenchmarkRunner` | Register, execute, and certify benchmark functions |
| `benchmark_runner.py` | `BenchmarkRunner.add()` | Register a callable with iteration count and threshold |
| `benchmark_runner.py` | `BenchmarkRunner.run()` | Execute all registered benchmarks; return `BenchmarkSuite` |
| `benchmark_runner.py` | `BenchmarkRunner.to_markdown()` | Render suite results as a markdown table |
| `benchmark_runner.py` | `BenchmarkResult` | Dataclass: `name`, `mean_ms`, `min_ms`, `max_ms`, `ops_per_sec`, `passed` |
| `benchmark_runner.py` | `BenchmarkSuite` | Dataclass: `name`, `results`, `total_ms`, `all_passed` |
| `benchmark_comparison.py` | `compute_delta()` | Compute `BenchmarkDelta` between two values with direction awareness |
| `benchmark_comparison.py` | `BenchmarkDelta` | Dataclass: `before`, `after`, `absolute_delta`, `relative_delta`, `improved` |
| `benchmark_comparison.py` | `mean()` | Arithmetic mean; returns 0.0 for empty list |
| `benchmark_comparison.py` | `stddev()` | Sample standard deviation; returns 0.0 for fewer than 2 values |
| `benchmark_comparison.py` | `coefficient_of_variation()` | CV as percentage; returns 0.0 if mean is zero |

## Operating Contracts

- `BenchmarkRunner.run()` uses `time.monotonic()` for wall-clock timing -- not CPU time.
- Each iteration calls the registered callable once with no arguments.
- `threshold_ms=0.0` (default) disables threshold checking; the benchmark always passes.
- `BenchmarkResult.passed` is `True` when `mean_ms <= threshold_ms` or threshold is 0.
- `compute_delta()` defaults to `higher_is_better=False` (lower values = improvement).
- `stddev()` uses sample standard deviation (Bessel's correction: divides by n-1).
- All functions are pure stdlib; no external dependencies.

## Integration Points

- **Depends on**: stdlib only (`time`, `math`, `dataclasses`, `collections.abc`)
- **Used by**: `codomyrmex.performance` top-level, `performance.mcp_tools` (`performance_compare_benchmarks`), CI benchmark pipelines

## Navigation

- **Parent**: [performance](../README.md)
- **Sibling**: [analysis](../analysis/AGENTS.md)
- **Root**: [codomyrmex](../../../../README.md)
