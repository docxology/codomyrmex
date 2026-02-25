# Concurrency - API Specification

## Introduction

The Concurrency module provides distributed locks, semaphores, and other synchronization primitives for coordinating access to shared resources in distributed systems.

## Endpoints / Functions / Interfaces

### Class: `BaseLock`

- **Description**: Abstract base class for lock implementations.
- **Methods**:
    - `acquire(blocking: bool = True, timeout: float | None = None) -> bool`: Acquire the lock.
    - `release() -> None`: Release the lock.
    - `locked() -> bool`: Check if lock is held.
    - `__enter__() -> BaseLock`: Context manager entry.
    - `__exit__(...) -> None`: Context manager exit.

### Class: `LocalLock`

- **Description**: In-process lock using threading primitives.
- **Constructor**:
    - `name` (str, optional): Lock identifier.
- **Methods**: Inherits from `BaseLock`.

### Class: `RedisLock`

- **Description**: Distributed lock using Redis for coordination.
- **Constructor**:
    - `name` (str): Lock name/key in Redis.
    - `redis_client`: Redis client instance.
    - `ttl` (int, optional): Lock TTL in seconds. Default: 30.
    - `retry_delay` (float, optional): Delay between acquisition retries.
- **Methods**:
    - `acquire(blocking: bool = True, timeout: float | None = None) -> bool`: Acquire distributed lock.
    - `release() -> None`: Release distributed lock.
    - `extend(additional_time: int) -> bool`: Extend lock TTL.
    - `locked() -> bool`: Check if lock is held by anyone.
    - `owned() -> bool`: Check if lock is held by current instance.

### Class: `BaseSemaphore`

- **Description**: Abstract base class for semaphore implementations.
- **Methods**:
    - `acquire(blocking: bool = True, timeout: float | None = None) -> bool`: Acquire a permit.
    - `release() -> None`: Release a permit.
    - `available() -> int`: Get number of available permits.

### Class: `LocalSemaphore`

- **Description**: In-process semaphore using threading primitives.
- **Constructor**:
    - `value` (int): Initial permit count. Default: 1.
    - `name` (str, optional): Semaphore identifier.
- **Methods**: Inherits from `BaseSemaphore`.

### Class: `LockManager`

- **Description**: Manages multiple named locks with automatic cleanup.
- **Constructor**:
    - `backend` (str, optional): Lock backend ("local" or "redis"). Default: "local".
    - `redis_client` (optional): Redis client for distributed locks.
- **Methods**:
    - `get_lock(name: str) -> BaseLock`: Get or create a named lock.
    - `acquire_all(names: list[str], timeout: float | None = None) -> bool`: Acquire multiple locks atomically.
    - `release_all(names: list[str]) -> None`: Release multiple locks.
    - `cleanup() -> None`: Clean up expired/unused locks.

### Class: `ReadWriteLock`

- **Description**: Lock allowing multiple readers or single writer.
- **Constructor**:
    - `name` (str, optional): Lock identifier.
- **Methods**:
    - `acquire_read(blocking: bool = True, timeout: float | None = None) -> bool`: Acquire read lock.
    - `acquire_write(blocking: bool = True, timeout: float | None = None) -> bool`: Acquire write lock.
    - `release_read() -> None`: Release read lock.
    - `release_write() -> None`: Release write lock.
    - `reader() -> ContextManager`: Context manager for read access.
    - `writer() -> ContextManager`: Context manager for write access.

## Data Models

### Model: `LockInfo`
- `name` (str): Lock identifier.
- `owner` (str | None): Current owner ID.
- `acquired_at` (float | None): Acquisition timestamp.
- `ttl` (int | None): Time-to-live in seconds.

## Authentication & Authorization

Redis-based locks inherit authentication from the provided Redis client. Configure Redis client credentials appropriately.

## Rate Limiting

N/A - Locks are synchronization primitives, not rate-limited services.

## Versioning

This API follows semantic versioning. Breaking changes will be documented in the changelog.
