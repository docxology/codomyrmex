# Concurrency Module

**Version**: v0.1.7 | **Status**: Active

Distributed locks, semaphores, and synchronization primitives.


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

## Quick Start

```python
from codomyrmex.concurrency import (
    LocalLock, LockManager, ReadWriteLock, LocalSemaphore
)

# Local lock (thread-safe)
lock = LocalLock("resource-1")
with lock:
    # Critical section
    update_shared_resource()

# Lock manager for multiple resources
manager = LockManager()
with manager.acquire("database", timeout=5.0):
    run_database_operation()

# Read-write lock (multiple readers, exclusive writers)
rw_lock = ReadWriteLock()
with rw_lock.read():
    data = read_shared_data()
with rw_lock.write():
    write_shared_data(data)

# Semaphore for limiting concurrent access
sem = LocalSemaphore(max_concurrent=3)
with sem:
    # Only 3 concurrent executions allowed
    process_request()
```

## Redis Lock (Distributed)

```python
from codomyrmex.concurrency import RedisLock

lock = RedisLock("resource", redis_url="redis://localhost")
with lock:
    # Distributed critical section
    pass
```

## Exports

| Class | Description |
|-------|-------------|
| `LocalLock` | Thread-safe local lock |
| `RedisLock` | Redis-backed distributed lock |
| `LockManager` | Manage multiple named locks |
| `ReadWriteLock` | Multiple readers, single writer |
| `LocalSemaphore` | Limit concurrent access |


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
