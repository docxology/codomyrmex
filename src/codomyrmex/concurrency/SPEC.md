# concurrency - Functional Specification

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Purpose

The `concurrency` module provides a suite of synchronization primitives to ensure data integrity and resource fairness in multi-process and distributed environments.

## Design Principles

### Correctness

- Atomic lock acquisition and release.
- Support for re-entrant locking (where applicable).

### Robustness

- Automatic expiration of stale locks.
- Resilience to process crashes during lock held.

### Flexibility

- Swapable backends (Local, Redis, Etcd) without changing application code.
- Support for both synchronous and asynchronous usage.

## Functional Requirements

### Distributed Locking

- Acquire and release locks based on a unique string identifier.
- Configurable acquisition timeout and lock TTL (Time-to-Live).
- Methods for checking lock status and ownership.

### Semaphores

- Limit the number of concurrent participants to a specific value.
- Support for weighted acquisitions.

### Backend Support

- **Local**: File-based or shared memory locking for single-host multi-processing.
- **Redis**: High-performance distributed locking using the Redlock algorithm or simple SETNX.

## Interface Contracts

### `BaseLock`

- `acquire(timeout: float) -> bool`
- `release() -> None`
- `is_locked() -> bool`

### `DistributedLock` (extends BaseLock)

- `extend(ttl: float) -> bool`

### `ReadWriteLock`

- `acquire_read()`
- `release_read()`
- `acquire_write()`
- `release_write()`

### `LockManager`

- `register_lock(name: str, lock: BaseLock)`
- `acquire_all(names: List[str]) -> bool`
- `release_all(names: List[str]) -> None`
- `@property stats() -> LockStats`

## Quality Standards

- Stress tests for race conditions.
- Verification of lock cleanup on process termination.
- ≥80% test coverage.

## Navigation

- **Human Documentation**: [README.md](README.md)
- **Technical Documentation**: [AGENTS.md](AGENTS.md)
- **Repository Root**: [../../../README.md](../../../README.md)
