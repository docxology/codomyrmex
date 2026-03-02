# Codomyrmex Agents — src/codomyrmex/performance/analysis

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose

Memory leak detection and performance regression analysis. Provides `MemoryProfiler`
for gc-based object counting across execution phases, and `RegressionDetector` for
comparing benchmark measurements against stored baselines with configurable severity thresholds.

## Key Components

| File | Class / Function | Role |
|------|-----------------|------|
| `memory_profiler.py` | `MemoryProfiler` | Track memory across phases; gc-based snapshot + diff |
| `memory_profiler.py` | `MemoryProfiler.snapshot()` | Full gc traversal: collect, count all objects by type (top 20 types stored) |
| `memory_profiler.py` | `MemoryProfiler.snapshot_lightweight()` | No gc traversal; accepts manually provided object count |
| `memory_profiler.py` | `MemoryProfiler.diff()` | Compute `MemoryDelta` between two labeled snapshots |
| `memory_profiler.py` | `MemorySnapshot` | Dataclass: `label`, `timestamp`, `object_count`, `tracked_types` |
| `memory_profiler.py` | `MemoryDelta` | Dataclass: `object_delta`, `type_deltas`, `leak_suspected` |
| `regression_detector.py` | `RegressionDetector` | Compare `BenchmarkResult` against `Baseline`; return `RegressionReport` |
| `regression_detector.py` | `RegressionDetector.check()` | Single benchmark check; raises `KeyError` if no baseline registered |
| `regression_detector.py` | `RegressionDetector.check_all()` | Batch check; silently skips results with no matching baseline |
| `regression_detector.py` | `RegressionDetector.summary()` | Multi-line text report with ✓/⚠ flags |
| `regression_detector.py` | `BenchmarkResult` | Dataclass: `name`, `value`, `unit`, `higher_is_better`, `metadata` |
| `regression_detector.py` | `Baseline` | Dataclass: `mean`, `stddev`, `warning_threshold` (10%), `critical_threshold` (25%) |
| `regression_detector.py` | `RegressionSeverity` | Enum: `INFO`, `WARNING`, `CRITICAL` |

## Operating Contracts

- `MemoryProfiler.snapshot()` calls `gc.collect()` before traversal — ensures stable counts but is slow for large heaps.
- `MemoryDelta.leak_suspected` is `True` when `object_delta > leak_threshold` (default: 1000 objects).
- `RegressionDetector.check()` raises `KeyError` if no baseline exists for the benchmark name — callers must register baselines first via `set_baseline()` or `set_baselines()`.
- `check_all()` silently skips results with no matching baseline (no exception, no log); use `check()` directly when all results must have baselines.
- Deviation direction: `higher_is_better=True` → decrease = regression; `higher_is_better=False` (default) → increase = regression.
- Default thresholds: WARNING at 10% deviation, CRITICAL at 25% deviation.
- Errors must be logged via `logging_monitoring` before re-raising.

## Integration Points

- **Depends on**: stdlib only (`gc`, `dataclasses`, `enum`, `time`)
- **Used by**: `codomyrmex.performance` top-level, `performance.mcp_tools` (`performance_check_regression`, `performance_compare_benchmarks`), `performance.profiling.benchmark`

## Navigation

- **📁 Parent**: [performance](../README.md)
- **🏠 Root**: ../../../../README.md
