# Codomyrmex Agents — src/codomyrmex/concurrency/semaphores

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose

Resource throttling primitives for bounding concurrent access. Provides an abstract `BaseSemaphore` interface, a thread-safe `LocalSemaphore` wrapping `threading.Semaphore`, and an `AsyncLocalSemaphore` wrapping `asyncio.Semaphore` with a synchronous acquisition bridge for mixed sync/async contexts.

## Key Components

| File | Class / Function | Role |
|------|-----------------|------|
| `semaphore.py` | `BaseSemaphore` | ABC defining `acquire(timeout) -> bool` and `release()` |
| `semaphore.py` | `LocalSemaphore` | Thread-safe semaphore wrapping `threading.Semaphore` with timeout support |
| `semaphore.py` | `AsyncLocalSemaphore` | Asyncio-compatible semaphore with `acquire_async()` and a sync `acquire()` fallback that bridges to the event loop |

## Operating Contracts

- `BaseSemaphore.initial_value` records the capacity set at construction.
- `LocalSemaphore.acquire` delegates directly to `threading.Semaphore.acquire(timeout=)`.
- `AsyncLocalSemaphore.acquire` detects whether a running event loop exists: if so, falls back to a sync counter with a logged warning; if not, creates a temporary event loop for the async acquire.
- `AsyncLocalSemaphore.release` updates both the asyncio semaphore and the sync fallback counter.
- Errors must be logged via `logging_monitoring` before re-raising.

## Integration Points

- **Depends on**: `asyncio`, `threading` (standard library only)
- **Used by**: `concurrency.workers.pool` (for bounded concurrency), any module needing resource throttling

## Navigation

- **Parent**: [concurrency](../README.md)
- **Root**: [Root](../../../../README.md)
