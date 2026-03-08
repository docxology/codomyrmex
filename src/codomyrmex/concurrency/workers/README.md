# Concurrency Workers

> **codomyrmex v1.1.9** | March 2026

## Overview

Async worker infrastructure providing bounded concurrency primitives. Includes `AsyncWorkerPool` for managed parallel task execution with semaphore-based limits, `Channel` for Go-style CSP inter-task communication (buffered and unbuffered), and async-native rate limiters (`AsyncTokenBucket`, `AsyncSlidingWindow`) for controlling throughput in asyncio contexts.

## PAI Integration

| PAI Phase | Relevance | Usage |
|-----------|-----------|-------|
| EXECUTE | Primary | `AsyncWorkerPool.map()` runs agent subtasks in bounded parallel |
| EXECUTE | Supporting | `Channel` enables structured communication between concurrent agent tasks |
| EXECUTE | Supporting | Rate limiters throttle API calls to external services |
| OBSERVE | Secondary | `PoolStats` tracks submitted/completed/failed counts and total elapsed time |

## Key Exports

| Name | Type | Source | Purpose |
|------|------|--------|---------|
| `AsyncWorkerPool` | class | `pool.py` | Bounded async worker pool with semaphore concurrency control |
| `TaskResult` | dataclass | `pool.py` | Result from a pool task (success, result, error, elapsed_ms) |
| `PoolStats` | dataclass | `pool.py` | Aggregate statistics (submitted, completed, failed, total_elapsed_ms) |
| `Channel` | class | `channels.py` | Generic async channel for inter-task communication |
| `ChannelClosed` | exception | `channels.py` | Raised on operations against a closed channel |
| `select` | function | `channels.py` | Wait for the first available item from multiple channels |
| `AsyncTokenBucket` | class | `rate_limiter.py` | Token bucket rate limiter for burst + sustained rate control |
| `AsyncSlidingWindow` | class | `rate_limiter.py` | Sliding window rate limiter for fixed request-per-window limits |
| `RateLimitConfig` | dataclass | `rate_limiter.py` | Configuration (max_requests, window_seconds, burst_size) |

## Quick Start

```python
import asyncio
from codomyrmex.concurrency.workers import (
    AsyncTokenBucket,
    AsyncWorkerPool,
    Channel,
    select,
)

async def process_item(item: str) -> str:
    await asyncio.sleep(0.01)  # Simulate work
    return f"processed:{item}"

async def main():
    # Bounded parallel execution
    async with AsyncWorkerPool(max_workers=4, name="analyzer") as pool:
        results = await pool.map(process_item, ["a", "b", "c", "d", "e"])
        for r in results:
            print(f"{r.task_id}: {r.result} ({r.elapsed_ms:.1f}ms)")
        print(f"Stats: {pool.stats}")

    # Channel communication
    ch = Channel[str](capacity=3)
    await ch.send("hello")
    msg = await ch.receive()
    ch.close()

    # Rate limiting
    limiter = AsyncTokenBucket(rate=10.0, capacity=20)
    if await limiter.acquire(tokens=1, timeout=5.0):
        print("Request allowed")

asyncio.run(main())
```

## Architecture

```
concurrency/workers/
    __init__.py            # Re-exports from all submodules
    pool.py                # AsyncWorkerPool, TaskResult, PoolStats
    channels.py            # Channel, ChannelClosed, select()
    rate_limiter.py        # AsyncTokenBucket, AsyncSlidingWindow, RateLimitConfig
```

## Testing

```bash
uv run pytest src/codomyrmex/tests/unit/concurrency/ -v -k worker
```

## Navigation

- Parent: [concurrency](../README.md)
- AGENTS: [AGENTS.md](AGENTS.md)
- SPEC: [SPEC.md](SPEC.md)
- Project root: [codomyrmex](../../../../README.md)
