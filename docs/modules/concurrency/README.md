# Concurrency Module Documentation

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

The Concurrency module provides distributed locks, semaphores, and advanced synchronization primitives for the Codomyrmex platform. It supports both local (file-based and thread-based) and distributed (Redis-backed) locking strategies, along with a unified lock manager for multi-resource acquisition and a read-write lock for shared/exclusive access patterns.


## Installation

```bash
pip install codomyrmex
```

## Key Features

- **Distributed Locking**: Redis-backed locks using SETNX with TTL for distributed multi-process synchronization
- **Local File Locks**: File-based locks using `fcntl.flock` for local multi-process synchronization
- **Semaphores**: Thread-safe and asyncio-compatible semaphores for resource throttling
- **Lock Manager**: Orchestrates multiple locks with deadlock-safe multi-resource acquisition (sorted ordering)
- **Read-Write Lock**: In-process shared/exclusive lock for concurrent read access with exclusive write access
- **Context Manager Support**: All lock implementations support Python `with` statement usage
- **Lock Telemetry**: Lock manager tracks acquisition/release statistics via `LockStats`


## Key Components

### Locks

| Component | Description |
|-----------|-------------|
| `BaseLock` | Abstract base class defining the lock interface with `acquire()`, `release()`, and context manager support |
| `LocalLock` | File-based lock implementation using `fcntl.flock` for local multi-process synchronization with configurable timeout and retry interval |
| `RedisLock` | Distributed lock using Redis SETNX with TTL, atomic Lua-scripted release (owner verification), and `extend()` for TTL renewal |

### Semaphores

| Component | Description |
|-----------|-------------|
| `BaseSemaphore` | Abstract base class for semaphore implementations with `acquire()` and `release()` |
| `LocalSemaphore` | Thread-safe semaphore wrapper around `threading.Semaphore` with timeout support |

### Management

| Component | Description |
|-----------|-------------|
| `LockManager` | Orchestrates multiple named locks with `register_lock()`, `acquire_all()` (deadlock-safe sorted acquisition), `release_all()`, and telemetry via `stats` property |
| `ReadWriteLock` | In-process read-write lock allowing concurrent readers with exclusive writer access using condition variables |
| `LockStats` | Dataclass providing telemetry: total locks, total acquisitions, total releases, active locks |

## Quick Start

### Local File Lock

```python
from codomyrmex.concurrency import LocalLock

# Use as context manager
with LocalLock("my-resource") as lock:
    # Critical section - protected by file lock
    pass

# Manual acquire/release
lock = LocalLock("my-resource")
if lock.acquire(timeout=5.0):
    try:
        # Critical section
        pass
    finally:
        lock.release()
```

### Redis Distributed Lock

```python
import redis
from codomyrmex.concurrency import RedisLock

client = redis.Redis()
lock = RedisLock("shared-resource", redis_client=client, ttl=30)

with lock:
    # Distributed critical section
    lock.extend(60)  # Extend TTL if operation takes longer
```

### Multi-Resource Lock Manager

```python
from codomyrmex.concurrency import LockManager, LocalLock

manager = LockManager()
manager.register_lock("db", LocalLock("db"))
manager.register_lock("cache", LocalLock("cache"))

# Acquire multiple locks safely (sorted to prevent deadlocks)
if manager.acquire_all(["db", "cache"], timeout=10.0):
    try:
        # Both resources locked
        pass
    finally:
        manager.release_all(["db", "cache"])

# Check statistics
stats = manager.stats
print(f"Active locks: {stats.active_locks}")
```

### Read-Write Lock

```python
from codomyrmex.concurrency import ReadWriteLock

rwlock = ReadWriteLock()

# Multiple readers can access concurrently
rwlock.acquire_read()
try:
    # Read shared data
    pass
finally:
    rwlock.release_read()

# Writers get exclusive access
rwlock.acquire_write()
try:
    # Modify shared data
    pass
finally:
    rwlock.release_write()
```


## Testing

```bash
uv run python -m pytest src/codomyrmex/tests/ -k concurrency -v
```

## Related Modules

- [logging_monitoring](../logging_monitoring/) - Structured logging for lock contention diagnostics
- [telemetry](../telemetry/) - Observability integration for lock manager statistics
- [events](../events/) - Event-driven patterns that may coordinate with concurrency primitives

## Navigation

- **Source**: [src/codomyrmex/concurrency/](../../../src/codomyrmex/concurrency/)
- **Parent**: [docs/modules/](../README.md)
