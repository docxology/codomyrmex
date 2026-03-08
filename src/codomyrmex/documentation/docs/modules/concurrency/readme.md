# Concurrency Module

**Version**: v1.2.0 | **Status**: Active | **Last Updated**: March 2026

Distributed locks, semaphores, and synchronization primitives for multi-process and distributed environments.

## PAI Integration

| Algorithm Phase | Role | Tools Used |
|----------------|------|-----------|
| **EXECUTE** | Run parallel agent tasks with distributed locking | Direct Python import |
| **BUILD** | Parallelize build steps using semaphores and lock managers | Direct Python import |
| **OBSERVE** | Monitor concurrent task status and lock contention | Direct Python import |

PAI agents access this module via direct Python import through the MCP bridge. The Engineer agent uses `LockManager` and `LocalSemaphore` to coordinate parallel build and execution tasks safely across concurrent agent operations.

## Installation

```bash
uv add codomyrmex
```

Or for development:

```bash
uv sync
```

## Key Exports

### Classes
- **`BaseLock`** — Abstract base class for all lock implementations.
- **`LocalLock`** — File-based lock for local multi-process synchronization.
- **`LockStats`** — Statistics for lock manager telemetry.
- **`LockManager`** — Orchestrates multiple locks and provides multi-resource acquisition.
- **`ReadWriteLock`** — In-process Read-Write lock (shared/exclusive).
- **`RedisLock`** — Distributed lock using Redis SETNX and TTL.
- **`BaseSemaphore`** — Abstract base class for all semaphore implementations.
- **`LocalSemaphore`** — Local thread-safe semaphore wrapper.
- **`AsyncLocalSemaphore`** — Asyncio-compatible semaphore.
- **`AsyncWorkerPool`** — Managed pool for bounded async task execution.
- **`DeadLetterQueue`** — Persistent track-and-replay for failed operations.
- **`TaskQueue`** — Priority-based task queue with deduplication.
- **`Channel`** — Go-style async communication channels.

## Quick Start

```python
from codomyrmex.concurrency import (
    LocalLock, LockManager, ReadWriteLock, LocalSemaphore
)

# Local lock (thread-safe and process-safe)
lock = LocalLock("resource-1")
with lock:
    # Critical section
    update_shared_resource()

# Lock manager for multiple resources (deadlock-free)
manager = LockManager()
manager.register_lock("db", LocalLock("database"))
manager.register_lock("file", LocalLock("config_file"))

with manager.acquire_all(["db", "file"], timeout=5.0):
    run_synced_operation()

# Read-write lock (multiple readers, exclusive writers)
rw_lock = ReadWriteLock()
with rw_lock.read_lock():
    data = read_shared_data()
with rw_lock.write_lock():
    write_shared_data(data)

# Semaphore for limiting concurrent access
sem = LocalSemaphore(value=3)
with sem:
    # Only 3 concurrent executions allowed
    process_request()
```

## Redis Lock (Distributed)

```python
from redis import Redis
from codomyrmex.concurrency import RedisLock

redis_client = Redis.from_url("redis://localhost:6379")
lock = RedisLock("resource", redis_client, ttl=60)
with lock:
    # Distributed critical section
    pass
```

## Bounded Async Worker Pool

```python
import asyncio
from codomyrmex.concurrency import AsyncWorkerPool

async def fetch_url(url):
    # Fetch content
    return f"Content from {url}"

async def main():
    async with AsyncWorkerPool(max_workers=10) as pool:
        urls = ["http://api1.com", "http://api2.com", ...]
        results = await pool.map(fetch_url, urls)
        for r in results:
            print(f"ID: {r.task_id}, Success: {r.success}, Data: {r.result}")

asyncio.run(main())
```

## Exports

| Class | Description |
|-------|-------------|
| `LocalLock` | Thread-safe and process-safe local lock |
| `RedisLock` | Redis-backed distributed lock |
| `LockManager` | Manage multiple named locks safely |
| `ReadWriteLock` | Multiple readers, single writer |
| `LocalSemaphore` | Limit concurrent access to a resource |
| `AsyncLocalSemaphore` | Asyncio-compatible counting semaphore |
| `AsyncWorkerPool` | Managed pool for bounded async task execution |
| `DeadLetterQueue` | Track and replay failed operations |
| `TaskQueue` | Priority-based distributed task queue |
| `Channel` | Async communication primitives (CSP) |
| `AsyncTokenBucket` | Token-bucket rate limiting |

## Testing

```bash
uv run python -m pytest src/codomyrmex/tests/ -k concurrency -v
```

## Documentation

- [Module Documentation](../../../docs/modules/concurrency/README.md)
- [Agent Guide](../../../docs/modules/concurrency/AGENTS.md)
- [Specification](../../../docs/modules/concurrency/SPEC.md)

## Navigation

- [SPEC](SPEC.md) | [AGENTS](AGENTS.md) | [PAI](PAI.md)
