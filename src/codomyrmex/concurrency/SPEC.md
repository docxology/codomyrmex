# Concurrency Module - Functional Specification

**Version**: v1.2.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose

The `concurrency` module provides synchronization primitives to ensure data integrity and resource fairness in multi-process, multi-threaded, and distributed environments.

## Design Principles

### Correctness
- Atomic lock acquisition and release.
- Thread-safe and process-safe implementations.
- Support for re-entrant locking in local primitives.
- Deadlock prevention through sorting in multi-resource acquisition.

### Robustness
- Automatic expiration of stale distributed locks (TTL).
- Exception-safe context managers for guaranteed resource release.
- Comprehensive stats and telemetry for monitoring contention.

### Flexibility
- Swapable backends (Local, Redis) for various deployment scenarios.
- Unified interfaces for both synchronous and asynchronous usage.
- Standardized error handling and timeout behaviors.

## Functional Requirements

### Distributed Locking
- Acquire and release locks based on unique string identifiers.
- Configurable acquisition timeout and lock Time-to-Live (TTL).
- Re-entrant `LocalLock` implementation for local synchronization.
- Atomic `RedisLock` using Lua scripts for safe check-and-delete.

### Semaphores
- Limit the number of concurrent participants to a specific value.
- Support for synchronous and asynchronous (asyncio) acquisition.
- Graceful bridging between sync and async contexts.

### Task Management
- Bounded async execution with `AsyncWorkerPool`.
- Result aggregation and statistics for parallel task batches.
- Dead-letter queue support for tracking and replaying failed operations.
- Priority-based task queue with deduplication and retry logic.
- Strategy-based task scheduling (round-robin, least-loaded, affinity).

### Communication and Throttling
- Go-style channels for inter-task communication (buffered/unbuffered).
- Rate limiting primitives (token bucket, sliding window).

## Interface Contracts

### `BaseLock`
- `acquire(timeout: float = 10.0, retry_interval: float = 0.1) -> bool`
- `release() -> None`
- `is_held: bool`
- `__enter__ / __exit__`: Context manager support.

### `LocalLock` (extends BaseLock)
- `__init__(name: str, lock_dir: str = "/tmp/codomyrmex/locks")`

### `RedisLock` (extends BaseLock)
- `__init__(name: str, redis_client: Redis, ttl: int = 30)`
- `extend(additional_ttl: int) -> bool`
- `is_locked_externally() -> bool`

### `ReadWriteLock`
- `acquire_read(timeout: float = None) -> bool`
- `release_read() -> None`
- `acquire_write(timeout: float = None) -> bool`
- `release_write() -> None`
- `read_lock() -> ContextManager`
- `write_lock() -> ContextManager`

### `LockManager`
- `register_lock(name: str, lock: BaseLock)`
- `get_lock(name: str) -> BaseLock | None`
- `acquire_all(names: List[str], timeout: float = 10.0) -> bool`
- `release_all(names: List[str]) -> None`
- `list_locks() -> List[str]`
- `@property stats() -> LockStats`

### `BaseSemaphore`
- `acquire(timeout: float = 10.0) -> bool`
- `release() -> None`
- `__enter__ / __exit__`: Context manager support.

### `AsyncLocalSemaphore` (extends BaseSemaphore)
- `async acquire_async(timeout: float | None = None) -> bool`
- `async __aenter__ / __aexit__`: Async context manager support.

### `AsyncWorkerPool`
- `async with AsyncWorkerPool(max_workers: int) as pool:`
- `async map(coro_fn: Callable, items: List[Any]) -> List[TaskResult]`
- `async submit(coro_fn: Callable, *args, **kwargs) -> TaskResult`
- `async shutdown() -> None`
- `@property stats() -> PoolStats`

### `DeadLetterQueue`
- `add(operation: str, args: dict, error: str, metadata: dict) -> str`
- `list_entries(operation: str, since: datetime, include_replayed: bool) -> List[dict]`
- `replay(entry_id: str, callback: Callable) -> dict`
- `purge(before: datetime) -> int`

### `ResultAggregator`
- `add(result: TaskResult)`
- `add_batch(results: List[TaskResult])`
- `aggregate() -> AggregateResult`
- `clear()`

### `TaskQueue`
- `enqueue(task: Task) -> bool`
- `dequeue() -> Task | None`
- `ack(task_id: str) -> bool`
- `nack(task_id: str) -> bool`
- `requeue_dead_letters() -> int`

### `TaskScheduler`
- `register_worker(worker_id: str, capabilities: List[str], max_concurrent: int)`
- `assign(task: Task) -> str`
- `report_completion(worker_id: str)`
- `rebalance() -> List[tuple]`

### `Channel`
- `async send(item: T, timeout: float | None = None)`
- `async receive(timeout: float | None = None) -> T`
- `close()`
- `async __aiter__`

### `AsyncTokenBucket`
- `async acquire(tokens: int = 1, timeout: float | None = None) -> bool`

### `AsyncSlidingWindow`
- `async acquire(timeout: float | None = None) -> bool`

## Quality Standards
- Comprehensive unit tests with ≥80% coverage.
- Zero traditional mocks (using `fakeredis` for Redis tests).
- Verified thread-safety and process-safety through stress tests.
- Clear documentation for each primitive and usage pattern.

## Navigation

- [README.md](README.md) | [AGENTS.md](AGENTS.md) | [PAI.md](PAI.md)
