# Codomyrmex Agents — src/codomyrmex/concurrency/tasks

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose

Task queue, scheduling, and worker execution for concurrent workloads. Provides a priority-based `TaskQueue` with deduplication, dead-letter handling, and at-least-once delivery semantics; a `TaskScheduler` with round-robin, least-loaded, and affinity-based routing; and a `TaskWorker` with error isolation and timeout support.

## Key Components

| File | Class / Function | Role |
|------|-----------------|------|
| `task_queue.py` | `TaskPriority` | Enum: CRITICAL(0), HIGH(1), NORMAL(2), LOW(3), BACKGROUND(4) |
| `task_queue.py` | `TaskStatus` | Enum: PENDING, IN_FLIGHT, COMPLETED, FAILED, DEAD_LETTER |
| `task_queue.py` | `Task` | Dataclass: task_id (auto-generated UUID), task_type, payload, priority, deadline, max_retries, retry_count, status |
| `task_queue.py` | `QueueEntry` | Internal heapq entry ordered by (priority, deadline, sequence) |
| `task_queue.py` | `TaskQueue` | Priority queue with dedup via `_seen_ids`, in-flight tracking, dead-letter queue, ack/nack protocol |
| `task_scheduler.py` | `SchedulingStrategy` | Enum: ROUND_ROBIN, LEAST_LOADED, AFFINITY |
| `task_scheduler.py` | `WorkerInfo` | Dataclass: worker_id, capabilities, max_concurrent, current_load |
| `task_scheduler.py` | `TaskScheduler` | Assigns tasks to workers; filters by capabilities and max_concurrent; supports affinity map |
| `task_worker.py` | `TaskResult` | Dataclass: task_id, worker_id, success, result, error, duration_ms, timestamp |
| `task_worker.py` | `TaskWorker` | Processes tasks with error isolation; failures captured in `TaskResult`, not propagated |

## Operating Contracts

- `TaskQueue.enqueue` deduplicates by `task_id`; returns `False` for duplicates.
- `TaskQueue.dequeue` skips expired tasks (past deadline) and moves them to the dead-letter queue.
- `TaskQueue.nack` increments retry_count; dead-letters the task when `retry_count >= max_retries`.
- `TaskScheduler.acquire_all` (via `assign`) filters workers by capability match and load capacity.
- `TaskScheduler` sorts lock names during `_round_robin` to cycle through eligible workers deterministically.
- `TaskWorker.process_one` catches all exceptions and returns them in `TaskResult.error` -- never propagates.
- Errors must be logged via `logging_monitoring` before re-raising.

## Integration Points

- **Depends on**: `heapq`, `time`, `uuid`, `collections.abc` (standard library only)
- **Used by**: `concurrency.workers` (pool submits to workers), `orchestrator` (workflow task dispatch)

## Navigation

- **Parent**: [concurrency](../README.md)
- **Root**: [Root](../../../../README.md)
