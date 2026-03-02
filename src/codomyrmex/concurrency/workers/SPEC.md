# Workers -- Technical Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

Async worker primitives: CSP-style channels for inter-task communication, a bounded worker pool for concurrent coroutine execution, and async rate limiters (token bucket and sliding window) for throughput control.

## Architecture

Three independent modules cooperate: `channels.py` provides Go-style communication, `pool.py` provides bounded execution, and `rate_limiter.py` provides throughput control. All are asyncio-native and use `asyncio.Lock`/`asyncio.Semaphore` for internal synchronization.

## Key Classes

### `Channel[T]`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `__init__` | `capacity: int = 0` | -- | 0 = unbuffered (queue maxsize=1); >0 = buffered |
| `send` | `item: T, timeout: float \| None` | `None` (async) | Put item; raises `ChannelClosed` if closed |
| `receive` | `timeout: float \| None` | `T` (async) | Get item; raises `ChannelClosed` if closed and empty |
| `close` | none | `None` | Prevent further sends; remaining items can still be received |
| `closed` (prop) | -- | `bool` | Whether the channel is closed |
| `__aiter__` | -- | async iterator | Yields items until closed and drained |

### `select`

| Parameter | Type | Description |
|-----------|------|-------------|
| `*channels` | `Channel` | Variable number of channels to listen on |
| `timeout` | `float \| None` | Max wait time |
| returns | `tuple[int, Any]` | `(channel_index, item)` for first ready channel |

### `AsyncWorkerPool`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `__init__` | `max_workers: int = 4, name: str` | -- | Creates `asyncio.Semaphore(max_workers)` |
| `submit` | `coro_fn, *args, task_id, **kwargs` | `TaskResult` (async) | Execute one coroutine under semaphore |
| `map` | `coro_fn, items: list` | `list[TaskResult]` (async) | Apply coro to items concurrently; preserves order |
| `shutdown` | none | `None` (async) | Prevent new submissions; await pending tasks |
| `stats` (prop) | -- | `PoolStats` | Submitted/completed/failed/elapsed counters |
| `__aenter__` / `__aexit__` | -- | -- | Async context manager; calls `shutdown` on exit |

### `AsyncTokenBucket`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `__init__` | `rate: float, capacity: int \| None` | -- | Tokens per second; capacity defaults to `int(rate)` |
| `acquire` | `tokens: int = 1, timeout: float \| None` | `bool` (async) | Wait for tokens; refills based on elapsed time |

### `AsyncSlidingWindow`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `__init__` | `max_requests: int, window_seconds: float` | -- | Max requests within the rolling window |
| `acquire` | `timeout: float \| None` | `bool` (async) | Check and record request; prunes expired timestamps |

## Dependencies

- **Internal**: None
- **External**: Standard library only (`asyncio`, `time`, `logging`, `dataclasses`)

## Constraints

- `Channel` internally uses `asyncio.Queue(maxsize=max(1, capacity))` -- unbuffered channels still use maxsize=1.
- `select` cancels all pending receive tasks after the first completes.
- `AsyncWorkerPool.submit` catches all exceptions from coroutines and wraps them in `TaskResult`.
- `AsyncTokenBucket._refill` caps tokens at capacity; uses `time.monotonic` for clock source.
- `AsyncSlidingWindow` prunes timestamps on every `acquire` call (O(n) per call).
- Zero-mock: real data only, `NotImplementedError` for unimplemented paths.

## Error Handling

- `Channel.send` raises `ChannelClosed` on closed channel.
- `Channel.receive` raises `ChannelClosed` if channel is closed and empty.
- `select` raises `asyncio.TimeoutError` if no channel is ready within timeout.
- `AsyncWorkerPool.submit` raises `RuntimeError` after shutdown; task failures are captured, not propagated.
- Pool task failures logged as warnings via module logger.
- All errors logged before propagation.
