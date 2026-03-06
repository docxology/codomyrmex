# Concurrency Module - Agent Guidelines

**Version**: v1.2.0 | **Status**: Active | **Last Updated**: March 2026

## Module Overview

The `concurrency` module provides thread-safe and process-safe synchronization primitives for coordinating parallel tasks.

## Key Classes

- **`LocalLock`** — Thread-safe and process-safe file-based lock. Supports re-entry.
- **`RedisLock`** — Redis-backed distributed lock for multi-node coordination.
- **`LockManager`** — Orchestrates multiple named locks to prevent deadlocks.
- **`ReadWriteLock`** — Efficient in-process lock (multiple readers, exclusive writer).
- **`LocalSemaphore`** — Limit concurrent access to resources.
- **`AsyncLocalSemaphore`** — Asyncio-compatible semaphore with sync bridge.
- **`AsyncWorkerPool`** — Managed pool for bounded async task execution.
- **`Channel`** — Go-style async communication channels for inter-task coordination.
- **`TaskQueue`** — Priority-based task queue with deduplication and dead-letter support.

## Agent Instructions

1. **Always Use Context Managers** — Prefer the `with lock:` or `async with sem:` patterns for guaranteed cleanup.
2. **Set Timeouts** — Never block indefinitely. Always provide a `timeout` argument to `acquire()` calls to prevent system-wide deadlocks.
3. **Prefer the LockManager** — When acquiring multiple locks, use `LockManager.acquire_all()` which handles resource sorting to prevent circular wait deadlocks.
4. **Choose the Right Primitive**:
   - Use `LocalLock` for local process synchronization.
   - Use `RedisLock` for distributed systems.
   - Use `ReadWriteLock` for data structures that are frequently read but rarely updated.
   - Use `AsyncWorkerPool` for limiting concurrency of async tasks (e.g., API calls).
   - Use `Channel` for message passing between async tasks.
   - Use `TaskQueue` for managing work that requires priority, deduplication, or retries.

## Common Patterns

### Safe Multi-Resource Acquisition
```python
from codomyrmex.concurrency import LockManager, LocalLock

manager = LockManager()
manager.register_lock("db", LocalLock("database"))
manager.register_lock("file", LocalLock("log_file"))

# Safely acquire both in sorted order
if manager.acquire_all(["file", "db"], timeout=5.0):
    try:
        # Critical section
        pass
    finally:
        manager.release_all(["db", "file"])
```

### Bounded Async Execution
```python
from codomyrmex.concurrency import AsyncWorkerPool

async def process_data(item):
    # Process item
    return item * 2

async with AsyncWorkerPool(max_workers=5) as pool:
    results = await pool.map(process_data, range(20))
    # results is a list of TaskResult objects
```

### Async Channels (CSP Pattern)
```python
import asyncio
from codomyrmex.concurrency import Channel

async def producer(ch: Channel):
    for i in range(5):
        await ch.send(f"msg-{i}")
    ch.close()

async def consumer(ch: Channel):
    async for msg in ch:
        print(f"Received: {msg}")

async def main():
    ch = Channel(capacity=2)
    await asyncio.gather(producer(ch), consumer(ch))
```

### Redis Distributed Locking
```python
from redis import Redis
from codomyrmex.concurrency import RedisLock

redis_client = Redis.from_url("redis://localhost:6379")
lock = RedisLock("global_task", redis_client, ttl=60)

with lock:
    # Exclusive distributed operation
    pass
```

## Testing Guidelines

- **Zero-Mock Policy**: Use `fakeredis.FakeRedis()` for testing Redis-dependent code instead of mocking the Redis client.
- **Race Conditions**: When testing concurrency, use multiple threads/processes and verify consistency of shared state.
- **Timeouts**: Verify that `TimeoutError` is raised (or `False` is returned) when locks cannot be acquired.

## Navigation

- [README.md](README.md) | [SPEC.md](SPEC.md) | [PAI.md](PAI.md)
