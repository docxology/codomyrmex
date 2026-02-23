# Agent Guidelines - Concurrency

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

## Module Overview

Thread pools, locks, semaphores, and distributed locking.

## Key Classes

- **Lock** — Basic thread lock
- **DistributedLock** — Cross-process locking
- **RedisLock** — Redis-backed distributed lock
- **Semaphore** — Counting semaphore
- **LockManager** — Manage multiple locks

## Agent Instructions

1. **Use context managers** — Always use `with lock:` pattern
2. **Set timeouts** — Avoid deadlocks with lock timeouts
3. **Prefer distributed** — Use `RedisLock` for multi-process
4. **Limit concurrency** — Use `Semaphore` for resource limits
5. **Name locks** — Use descriptive names for debugging

## Common Patterns

```python
from codomyrmex.concurrency import Lock, Semaphore, RedisLock, LockManager

# Basic locking
lock = Lock("resource_lock")
with lock:
    modify_shared_resource()

# Semaphore for limited concurrency
sem = Semaphore("api_calls", limit=10)
with sem:
    call_rate_limited_api()

# Distributed locking
redis_lock = RedisLock("global_lock", redis_url="redis://localhost")
with redis_lock.acquire(timeout=5.0):
    perform_exclusive_operation()

# Lock manager for multiple resources
manager = LockManager()
with manager.acquire_all(["lock_a", "lock_b"]):
    modify_multiple_resources()
```

## Testing Patterns

```python
# Verify lock exclusion
lock = Lock("test")
lock.acquire()
assert not lock.acquire(timeout=0.1)  # Should fail
lock.release()

# Verify semaphore counting
sem = Semaphore("test", limit=2)
assert sem.acquire()
assert sem.acquire()
assert not sem.acquire(timeout=0.1)  # At limit
```

## Navigation

- [README](README.md) | [SPEC](SPEC.md) | [PAI](PAI.md)
