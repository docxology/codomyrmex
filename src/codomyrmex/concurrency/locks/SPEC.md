# Locks -- Technical Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

Provides lock primitives spanning local file-based locking, Redis-backed distributed locking, multi-resource deadlock-safe acquisition, and in-process reader/writer synchronization.

## Architecture

All locks extend `BaseLock` (ABC) which defines `acquire`/`release` and a context manager protocol. `LockManager` composes multiple `BaseLock` instances and sorts by name before bulk acquisition to prevent deadlocks. `ReadWriteLock` is standalone, using `threading.Condition` for shared/exclusive semantics.

## Key Classes

### `BaseLock` (ABC)

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `acquire` | `timeout: float = 10.0, retry_interval: float = 0.1` | `bool` | Acquire the lock within timeout |
| `release` | none | `None` | Release the lock |
| `__enter__` | none | `self` | Acquires lock; raises `TimeoutError` on failure |
| `__exit__` | exc args | `None` | Releases lock |

### `LocalLock`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `__init__` | `name: str, lock_dir: str = "/tmp/codomyrmex/locks"` | -- | Creates lock directory if missing |
| `acquire` | `timeout: float, retry_interval: float` | `bool` | Uses `fcntl.flock(LOCK_EX \| LOCK_NB)` with retry loop |
| `release` | none | `None` | Unlocks via `fcntl.LOCK_UN`, closes file, removes lock file |

### `RedisLock`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `__init__` | `name: str, redis_client: redis.Redis, ttl: int = 30` | -- | Generates UUID owner_id; key is `codomyrmex:lock:{name}` |
| `acquire` | `timeout: float, retry_interval: float` | `bool` | Uses `SET NX EX` for atomic acquire with TTL |
| `release` | none | `None` | Lua script: check owner_id then DEL (atomic) |
| `extend` | `additional_ttl: int` | `bool` | Lua script: check owner_id then EXPIRE |

### `LockManager`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `register_lock` | `name: str, lock: BaseLock` | `None` | Register a lock by name |
| `acquire_all` | `names: list[str], timeout: float` | `bool` | Sort names, acquire in order; rollback on failure |
| `release_all` | `names: list[str]` | `None` | Release all named locks |
| `stats` (property) | none | `LockStats` | Acquisition/release counters and active count |

### `ReadWriteLock`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `acquire_read` | none | `None` | Wait until no writers, increment reader count |
| `release_read` | none | `None` | Decrement reader count; notify if last reader |
| `acquire_write` | none | `None` | Wait until no readers and no writers |
| `release_write` | none | `None` | Decrement writer count; notify all |

## Dependencies

- **Internal**: `codomyrmex.logging_monitoring.core.logger_config`
- **External**: `fcntl` (Unix), `threading`, `redis` (optional)

## Constraints

- `LocalLock` uses `fcntl.flock` -- Unix/macOS only (not available on Windows).
- `RedisLock` requires the `redis` Python package; import is guarded with try/except in `__init__.py`.
- `LockManager.acquire_all` sorts names to impose a global lock ordering.
- Zero-mock: real data only, `NotImplementedError` for unimplemented paths.

## Error Handling

- `BaseLock.__enter__` raises `TimeoutError` if `acquire()` returns `False`.
- `LockManager.acquire_all` logs error and releases any already-acquired locks on failure.
- `LocalLock.release` logs at DEBUG level if lock file removal fails (non-fatal).
- All errors logged before propagation.
