# Performance Benchmarking

**Version**: v1.0.8 | **Status**: Active | **Last Updated**: March 2026

## Overview

Benchmark execution and comparison submodule. `BenchmarkRunner` executes timed
iterations of callable functions, collects per-benchmark statistics (mean, min,
max, ops/s), and certifies results against configurable thresholds.
`benchmark_comparison` provides statistical helpers for computing deltas,
standard deviation, and coefficient of variation across benchmark runs.

## PAI Integration

| PAI Phase | Usage |
|-----------|-------|
| VERIFY | Run benchmark suites and certify against thresholds |
| EXECUTE | Compare benchmark results across commits or environments |

## Key Exports

| Symbol | Type | Source |
|--------|------|--------|
| `BenchmarkRunner` | class | `benchmark_runner.py` |
| `BenchmarkResult` | dataclass | `benchmark_runner.py` |
| `BenchmarkSuite` | dataclass | `benchmark_runner.py` |
| `BenchmarkDelta` | dataclass | `benchmark_comparison.py` |
| `compute_delta` | function | `benchmark_comparison.py` |
| `mean` | function | `benchmark_comparison.py` |
| `stddev` | function | `benchmark_comparison.py` |
| `coefficient_of_variation` | function | `benchmark_comparison.py` |

## Quick Start

```python
from codomyrmex.performance.benchmarking import BenchmarkRunner, compute_delta

# Run a benchmark suite
runner = BenchmarkRunner(suite_name="Sort Suite")
runner.add("sort_1000", lambda: sorted(range(1000, 0, -1)), threshold_ms=1.0)
suite = runner.run()
assert suite.all_passed
print(runner.to_markdown(suite))

# Compare two measurements
delta = compute_delta("sort_1000", before=0.85, after=0.72)
assert delta.improved  # lower is better by default
```

## Architecture

```
benchmarking/
  __init__.py                # Re-exports from both submodules
  benchmark_runner.py        # BenchmarkRunner, BenchmarkResult, BenchmarkSuite
  benchmark_comparison.py    # BenchmarkDelta, compute_delta, mean, stddev, coefficient_of_variation
```

## Testing

```bash
uv run pytest src/codomyrmex/tests/unit/performance/ -k "benchmark"
```

## Navigation

- **Parent**: [performance](../README.md)
- **Sibling**: [analysis](../analysis/README.md)
- **Root**: [codomyrmex](../../../../README.md)
