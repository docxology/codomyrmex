# Performance Analysis

**Version**: v1.1.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

Memory leak detection and performance regression analysis submodule. Provides
`MemoryProfiler` for gc-based object counting across execution phases, and
`RegressionDetector` for comparing benchmark measurements against stored
baselines with configurable severity thresholds (WARNING at 10%, CRITICAL at 25%).

## PAI Integration

| PAI Phase | Usage |
|-----------|-------|
| VERIFY | Detect memory leaks and performance regressions in CI |
| EXECUTE | Run regression checks against stored baselines |

## Key Exports

| Symbol | Type | Source |
|--------|------|--------|
| `MemoryProfiler` | class | `memory_profiler.py` |
| `MemorySnapshot` | dataclass | `memory_profiler.py` |
| `MemoryDelta` | dataclass | `memory_profiler.py` |
| `RegressionDetector` | class | `regression_detector.py` |
| `BenchmarkResult` | dataclass | `regression_detector.py` |
| `Baseline` | dataclass | `regression_detector.py` |
| `RegressionReport` | dataclass | `regression_detector.py` |
| `RegressionSeverity` | enum | `regression_detector.py` |

## Quick Start

```python
from codomyrmex.performance.analysis import MemoryProfiler, RegressionDetector, Baseline, BenchmarkResult

# Memory leak detection
profiler = MemoryProfiler(leak_threshold=1000)
profiler.snapshot("before")
# ... do work ...
profiler.snapshot("after")
delta = profiler.diff("before", "after")
assert not delta.leak_suspected

# Regression detection
detector = RegressionDetector()
detector.set_baseline(Baseline("import_time", mean=120.0, stddev=5.0))
result = BenchmarkResult("import_time", value=155.0, unit="ms")
report = detector.check(result)
if report.is_regression:
    print(report.message)
```

## Architecture

```
analysis/
  __init__.py              # Re-exports from both submodules
  memory_profiler.py       # MemoryProfiler, MemorySnapshot, MemoryDelta
  regression_detector.py   # RegressionDetector, BenchmarkResult, Baseline, RegressionReport
```

## Testing

```bash
uv run pytest src/codomyrmex/tests/unit/performance/ -k "analysis or memory or regression"
```

## Navigation

- **Parent**: [performance](../README.md)
- **Sibling**: [benchmarking](../benchmarking/README.md)
- **Root**: [codomyrmex](../../../../README.md)
