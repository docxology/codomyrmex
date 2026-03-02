# Semaphores -- Technical Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

Provides counting semaphore primitives for resource throttling. Two concrete implementations cover threaded (`LocalSemaphore`) and asyncio (`AsyncLocalSemaphore`) contexts, both extending `BaseSemaphore`.

## Architecture

`BaseSemaphore` defines the contract (`acquire`/`release`). `LocalSemaphore` is a thin wrapper around `threading.Semaphore`. `AsyncLocalSemaphore` wraps `asyncio.Semaphore` and includes a sync-to-async bridge for mixed contexts.

## Key Classes

### `BaseSemaphore` (ABC)

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `__init__` | `value: int = 1` | -- | Sets `initial_value` |
| `acquire` | `timeout: float = 10.0` | `bool` | Acquire one unit within timeout |
| `release` | none | `None` | Release one unit |

### `LocalSemaphore`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `__init__` | `value: int = 1` | -- | Creates `threading.Semaphore(value)` |
| `acquire` | `timeout: float = 10.0` | `bool` | Delegates to `threading.Semaphore.acquire(timeout=)` |
| `release` | none | `None` | Delegates to `threading.Semaphore.release()` |

### `AsyncLocalSemaphore`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `__init__` | `value: int = 1` | -- | Creates `asyncio.Semaphore(value)` and a sync fallback counter |
| `acquire_async` | none | `None` (async) | Awaits `asyncio.Semaphore.acquire()` |
| `acquire` | `timeout: float = 10.0` | `bool` | Sync bridge: uses fallback counter if inside event loop, else creates temporary loop |
| `release` | none | `None` | Releases asyncio semaphore and increments sync counter if below initial_value |

## Dependencies

- **Internal**: None
- **External**: Standard library only (`asyncio`, `threading`, `abc`, `logging`)

## Constraints

- `AsyncLocalSemaphore.acquire` from an async context uses a degraded sync counter path (logs a warning).
- The temporary event loop created by sync `acquire` is closed and unset after use.
- Zero-mock: real data only, `NotImplementedError` for unimplemented paths.

## Error Handling

- `AsyncLocalSemaphore.acquire` catches `RuntimeError` (no running loop) to select the correct acquisition path.
- Timeout exceeded during async acquire is caught as `asyncio.TimeoutError` and logged as a warning.
- Generic exceptions during sync acquire are caught, logged as errors, and return `False`.
- All errors logged before propagation.
