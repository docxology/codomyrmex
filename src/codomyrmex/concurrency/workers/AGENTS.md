# Codomyrmex Agents — src/codomyrmex/concurrency/workers

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose

Async worker infrastructure for concurrent operations. Provides Go-style `Channel` communication (buffered/unbuffered with `select`), an `AsyncWorkerPool` with semaphore-bounded concurrency and `map`/`submit` APIs, and async rate limiters (`AsyncTokenBucket`, `AsyncSlidingWindow`) for throttling.

## Key Components

| File | Class / Function | Role |
|------|-----------------|------|
| `channels.py` | `Channel[T]` | Generic async channel with `send`/`receive`, buffered/unbuffered modes, close semantics, and async iteration |
| `channels.py` | `ChannelClosed` | Exception raised on operations against a closed channel |
| `channels.py` | `select` | Await the first available item from multiple channels; returns `(index, item)` tuple |
| `pool.py` | `AsyncWorkerPool` | Bounded async worker pool using `asyncio.Semaphore`; supports `submit`, `map`, `shutdown`, and async context manager |
| `pool.py` | `TaskResult` | Dataclass: task_id, success, result, error, elapsed_ms |
| `pool.py` | `PoolStats` | Dataclass: submitted, completed, failed, total_elapsed_ms |
| `rate_limiter.py` | `RateLimitConfig` | Dataclass: max_requests, window_seconds, burst_size |
| `rate_limiter.py` | `AsyncTokenBucket` | Token bucket rate limiter with configurable rate and burst capacity |
| `rate_limiter.py` | `AsyncSlidingWindow` | Sliding window rate limiter tracking request timestamps |

## Operating Contracts

- `Channel.send` raises `ChannelClosed` if the channel has been closed; `receive` raises it if closed and empty.
- `Channel.__aiter__` yields items until the channel is closed and drained.
- `AsyncWorkerPool.submit` raises `RuntimeError` after `shutdown()` is called.
- `AsyncWorkerPool` uses `asyncio.Semaphore(max_workers)` to bound concurrency.
- `AsyncTokenBucket` refills tokens based on elapsed time since last refill; capped at capacity.
- `AsyncSlidingWindow` prunes timestamps older than the window on each `acquire` call.
- Errors must be logged via `logging_monitoring` before re-raising.

## Integration Points

- **Depends on**: `asyncio`, `time`, `logging` (standard library only)
- **Used by**: `orchestrator.execution`, any module needing bounded async concurrency or inter-task communication

## Navigation

- **Parent**: [concurrency](../README.md)
- **Root**: [Root](../../../../README.md)
