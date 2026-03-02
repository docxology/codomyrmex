# Codomyrmex Agents — src/codomyrmex/model_ops/optimization

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose

Inference optimization sub-module providing request batching, LRU result caching, and a unified `InferenceOptimizer` engine. Designed to reduce model inference latency and compute cost through intelligent batching, cache-hit avoidance, and performance statistics tracking.

## Key Components

| File | Class / Function | Role |
|------|-----------------|------|
| `models.py` | `QuantizationType` | Enum: FP32, FP16, INT8, INT4 |
| `models.py` | `BatchingStrategy` | Enum: FIXED, DYNAMIC, ADAPTIVE |
| `models.py` | `OptimizationConfig` | Configuration dataclass: batch size, timeout, caching, worker count |
| `models.py` | `InferenceStats` | Statistics dataclass with `cache_hit_rate` property |
| `models.py` | `InferenceRequest` | Generic request dataclass with priority and age tracking |
| `models.py` | `InferenceResult` | Generic result dataclass with latency, cache flag, batch size |
| `batcher.py` | `RequestBatcher[T]` | Generic request batcher with background thread; collects items up to `max_batch_size` or `timeout_ms`, then calls processor callable |
| `cache.py` | `InferenceCache` | Thread-safe LRU cache with `max_size` eviction |
| `optimizer.py` | `InferenceOptimizer` | Main engine combining `InferenceCache` and `RequestBatcher`; supports single `infer()` and `infer_batch()` with automatic cache check |

## Operating Contracts

- `InferenceCache` uses `threading.Lock` for all mutations; LRU eviction removes the least-recently-accessed key.
- `RequestBatcher` runs a daemon thread via `start()`; must be `stop()`-ed for clean shutdown.
- `RequestBatcher._process_batch()` resolves all `Future` instances with the processor output, or sets exception on failure.
- `InferenceOptimizer.infer()` checks cache first (if enabled), then calls the model function, and caches the result.
- `InferenceOptimizer.infer_batch()` bypasses the batcher and calls the model function directly on the full input list.
- `InferenceOptimizer.stats` returns a snapshot of request counts, batch counts, cache hit/miss rates, and average latency.
- Errors must be logged via `logging_monitoring` before re-raising.

## Integration Points

- **Depends on**: Standard library only (`threading`, `queue`, `time`, `concurrent.futures`)
- **Used by**: ML serving pipelines requiring latency optimization

## Navigation

- **Parent**: [model_ops](../README.md)
- **Root**: [Root](../../../../README.md)
