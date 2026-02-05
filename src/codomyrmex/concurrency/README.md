# concurrency

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

The concurrency module provides distributed locks, semaphores, and synchronization primitives for coordinating access to shared resources across threads and processes. It includes file-based local locks, Redis-backed distributed locks, thread-safe and asyncio-compatible semaphores, and a lock manager that orchestrates multi-resource acquisition with deadlock avoidance.

## Key Exports

- **`BaseLock`** -- Abstract base class for all lock implementations. Defines the `acquire(timeout, retry_interval)` and `release()` contract, with context manager support (`with` statement).
- **`LocalLock`** -- File-based lock using `fcntl` for local multi-process synchronization. Stores lock files in `/tmp/codomyrmex/locks/` by default.
- **`BaseSemaphore`** -- Abstract base class for semaphore implementations. Defines `acquire(timeout)` and `release()` methods with configurable initial value.
- **`LocalSemaphore`** -- Thread-safe semaphore wrapper around `threading.Semaphore` for local resource throttling.
- **`RedisLock`** -- Distributed lock backed by Redis using atomic `SETNX` with TTL expiration. Supports owner-based release to prevent accidental unlock by other processes.
- **`LockManager`** -- Orchestrates multiple registered locks and provides `acquire_all()` with sorted acquisition order to avoid deadlocks. Exposes `LockStats` telemetry.
- **`ReadWriteLock`** -- Allows concurrent readers with exclusive writer access for read-heavy workloads.

## Directory Contents

- `__init__.py` - Module entry point; exports all lock and semaphore classes
- `distributed_lock.py` - `BaseLock` ABC and `LocalLock` file-based implementation
- `semaphore.py` - `BaseSemaphore` ABC, `LocalSemaphore`, and `AsyncLocalSemaphore` implementations
- `redis_lock.py` - `RedisLock` distributed lock using Redis SETNX with TTL
- `lock_manager.py` - `LockManager` for multi-lock orchestration and `ReadWriteLock` primitive
- `AGENTS.md` - Agent integration specification
- `API_SPECIFICATION.md` - Programmatic interface documentation
- `SPEC.md` - Module specification
- `PAI.md` - PAI integration notes

## Navigation

- **Full Documentation**: [docs/modules/concurrency/](../../../docs/modules/concurrency/)
- **Parent Directory**: [codomyrmex](../README.md)
- **Project Root**: ../../../README.md
