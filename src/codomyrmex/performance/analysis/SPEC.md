# Performance Analysis — Technical Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

Two-component analysis toolkit: `MemoryProfiler` for object-count-based leak detection
across execution phases, and `RegressionDetector` for statistical comparison of benchmark
results against stored baselines with configurable warning/critical thresholds.

## Architecture

Both components are standalone stateful classes with no external dependencies beyond
stdlib. `MemoryProfiler` uses Python's `gc` module for full-heap traversal.
`RegressionDetector` uses a dictionary-keyed baseline registry pattern.

## Key Classes

### `MemoryProfiler`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `snapshot(label)` | `label: str` | `MemorySnapshot` | Full gc traversal; calls `gc.collect()` first; stores top 20 types by count |
| `snapshot_lightweight(label, tracked_count)` | `label: str, tracked_count: int` | `MemorySnapshot` | No gc traversal; uses caller-supplied count |
| `diff(label_a, label_b)` | `str, str` | `MemoryDelta` | Computes object delta and per-type changes; sets `leak_suspected` if delta > threshold |
| `get_snapshot(label)` | `label: str` | `MemorySnapshot \| None` | Retrieve stored snapshot by label |

### `MemorySnapshot`

| Attribute | Type | Description |
|-----------|------|-------------|
| `label` | `str` | Snapshot identifier |
| `timestamp` | `float` | Unix timestamp when taken |
| `object_count` | `int` | Total gc-tracked objects |
| `tracked_types` | `dict[str, int]` | Top 20 type counts by frequency |

### `RegressionDetector`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `set_baseline(baseline)` | `Baseline` | `None` | Register or replace a baseline by name |
| `set_baselines(baselines)` | `list[Baseline]` | `None` | Batch register baselines |
| `check(result)` | `BenchmarkResult` | `RegressionReport` | Raises `KeyError` if baseline missing |
| `check_all(results)` | `list[BenchmarkResult]` | `list[RegressionReport]` | Skips results without baselines silently |
| `regressions_only(reports)` | `list[RegressionReport]` | `list[RegressionReport]` | Filter to is_regression=True only |
| `summary(reports)` | `list[RegressionReport]` | `str` | Multi-line ✓/⚠ text report |
| `clear()` | — | `None` | Remove all stored baselines |

### `Baseline`

| Attribute | Type | Default | Description |
|-----------|------|---------|-------------|
| `name` | `str` | — | Benchmark identifier (matches `BenchmarkResult.name`) |
| `mean` | `float` | — | Historical mean value |
| `stddev` | `float` | `0.0` | Historical standard deviation |
| `warning_threshold` | `float` | `0.10` | 10% relative deviation → WARNING |
| `critical_threshold` | `float` | `0.25` | 25% relative deviation → CRITICAL |

## Dependencies

- **Internal**: None (standalone analysis utilities)
- **External**: stdlib only — `gc`, `dataclasses`, `enum`, `time`

## Constraints

- `MemoryProfiler.snapshot()` is slow on large heaps (full gc traversal); prefer `snapshot_lightweight()` in hot paths.
- `leak_suspected` threshold defaults to 1000 objects; adjust via `MemoryProfiler(leak_threshold=N)`.
- Deviation direction is configurable: `higher_is_better=True` means a decrease from baseline is the regression.
- `check()` raises `KeyError` on missing baseline — do not call without first registering a baseline.
- `check_all()` silently skips unregistered benchmarks — callers must not rely on it for full coverage.
- Zero-mock: real gc data only; no simulated memory counts in production code.

## Error Handling

- `KeyError` raised by `check()` when benchmark name has no registered baseline.
- `diff()` returns an empty `MemoryDelta` (object_delta=0, no type_deltas) when either label is not found — no exception raised.
- All errors logged via `logging_monitoring` before propagation.
