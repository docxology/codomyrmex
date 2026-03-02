# Codomyrmex Agents — src/codomyrmex/concurrency/locks

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose

Distributed and local lock primitives for multi-process and multi-node synchronization. Provides an abstract `BaseLock` interface, a file-based `LocalLock` using `fcntl`, a Redis-backed `RedisLock` using SETNX with TTL and Lua-script atomic release, a `LockManager` for deadlock-safe multi-resource acquisition, and an in-process `ReadWriteLock` (shared/exclusive).

## Key Components

| File | Class / Function | Role |
|------|-----------------|------|
| `distributed_lock.py` | `BaseLock` | ABC defining `acquire(timeout, retry_interval) -> bool`, `release()`, and context manager protocol |
| `distributed_lock.py` | `LocalLock` | File-based lock using `fcntl.flock` (LOCK_EX/LOCK_NB) for local multi-process synchronization |
| `redis_lock.py` | `RedisLock` | Distributed lock using Redis `SET NX EX`; atomic owner-checked release via Lua script; supports `extend()` |
| `lock_manager.py` | `LockManager` | Orchestrates multiple `BaseLock` instances; `acquire_all` sorts by name to prevent deadlocks |
| `lock_manager.py` | `LockStats` | Dataclass tracking total_locks, total_acquisitions, total_releases, active_locks |
| `lock_manager.py` | `ReadWriteLock` | In-process shared/exclusive lock using `threading.Condition`; multiple readers or single writer |

## Operating Contracts

- `BaseLock.__enter__` raises `TimeoutError` if acquisition fails within the default timeout.
- `LocalLock` creates lock files under `/tmp/codomyrmex/locks/` by default; cleans up on release.
- `RedisLock.release` uses a Lua script to atomically check ownership before deletion (prevents releasing another client's lock).
- `LockManager.acquire_all` sorts lock names alphabetically to prevent deadlock; rolls back all acquired locks on any failure.
- `RedisLock` is conditionally imported; `RedisLock` is `None` if `redis` is not installed.
- Errors must be logged via `logging_monitoring` before re-raising.

## Integration Points

- **Depends on**: `codomyrmex.logging_monitoring.core.logger_config` (for `get_logger`), `redis` (optional, for `RedisLock`)
- **Used by**: `concurrency.tasks`, `concurrency.workers`, any module needing mutual exclusion

## Navigation

- **Parent**: [concurrency](../README.md)
- **Root**: [Root](../../../../README.md)
