# Codomyrmex Agents — concurrency

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Purpose

The `concurrency` module enables agents to safely coordinate access to shared state and resources. It provides the mechanism for mutual exclusion and resource limiting in complex, concurrent workflows.

## Active Components

- `distributed_lock.py` – Provides atomic mutual exclusion.
- `semaphore.py` – Manages shared resource quotas.
- `redis_lock.py` – Orchestrates locking across distributed agent nodes.

## Operating Contracts

1. **Deadlock Prevention**: Always use timeouts when acquiring locks.
2. **Deterministic Cleanup**: Ensure locks are released in a `finally` block or context manager.
3. **Hierarchy Aware**: Supports hierarchical locking for nested resource trees.

## Core Interfaces

- `Lockable`: Abstract interface for any resource that can be locked.
- `DistributedLock`: Interface for cross-process synchronization.
- `LockManager`: Multi-lock orchestration interface.
- `ReadWriteLock`: Shared/exclusive access interface.
- `Semaphore`: Interface for counting semaphores.

## Navigation Links

- **🏠 Project Root**: ../../../README.md
- **📦 Module README**: ./README.md
- **📜 Functional Spec**: ./SPEC.md
