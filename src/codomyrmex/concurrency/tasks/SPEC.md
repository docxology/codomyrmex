# Task Management -- Technical Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

Provides a complete task lifecycle: priority queuing with deduplication and dead-letter handling (`TaskQueue`), strategy-based worker assignment (`TaskScheduler`), and error-isolated task execution (`TaskWorker`).

## Architecture

Three cooperating classes form a pipeline: `TaskQueue` manages ordering and delivery guarantees, `TaskScheduler` routes tasks to workers based on configurable strategies, and `TaskWorker` executes tasks with error isolation. All classes are in-memory; persistence is delegated to callers.

## Key Classes

### `Task`

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `task_id` | `str` | auto-generated `task-{uuid}` | Unique identifier |
| `task_type` | `str` | `""` | Type for routing/capability matching |
| `payload` | `dict[str, Any]` | `{}` | Task data |
| `priority` | `TaskPriority` | `NORMAL` | Execution priority |
| `deadline` | `float` | `0.0` | Unix timestamp deadline (0 = no deadline) |
| `max_retries` | `int` | `3` | Maximum retry attempts |
| `retry_count` | `int` | `0` | Current retries |
| `status` | `TaskStatus` | `PENDING` | Current lifecycle status |

### `TaskQueue`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `enqueue` | `task: Task` | `bool` | Add task; dedup by task_id; returns False if duplicate |
| `dequeue` | none | `Task \| None` | Pop highest-priority task; skips expired to dead-letter |
| `ack` | `task_id: str` | `bool` | Mark task completed; remove from in-flight |
| `nack` | `task_id: str` | `bool` | Retry or dead-letter; True if requeued |
| `requeue_dead_letters` | none | `int` | Move all dead-letter tasks back; returns count |
| `pending_count` (prop) | -- | `int` | Number of queued tasks |
| `in_flight_count` (prop) | -- | `int` | Number of tasks being processed |
| `dead_letter_count` (prop) | -- | `int` | Number of dead-lettered tasks |

### `TaskScheduler`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `__init__` | `strategy: SchedulingStrategy` | -- | Default: ROUND_ROBIN |
| `register_worker` | `worker_id, capabilities, max_concurrent` | `None` | Add a worker to the pool |
| `unregister_worker` | `worker_id: str` | `bool` | Remove worker; True if found |
| `set_affinity` | `task_type: str, worker_id: str` | `None` | Route task_type to preferred worker |
| `assign` | `task: Task` | `str` | Returns worker_id or empty string if none available |
| `report_completion` | `worker_id: str` | `None` | Decrement worker's current_load |
| `rebalance` | none | `list[tuple[str, str]]` | Suggest (from, to) reassignments for load balancing |

### `TaskWorker`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `__init__` | `worker_id, handler: Callable, timeout_ms` | -- | Auto-generates worker_id if empty |
| `start` / `stop` | none | `None` | Toggle `_running` flag |
| `process_one` | `task: Task` | `TaskResult` | Execute handler with error isolation; captures exceptions in result |

## Dependencies

- **Internal**: None (self-contained within `concurrency`)
- **External**: Standard library only (`heapq`, `time`, `uuid`, `enum`, `dataclasses`)

## Constraints

- `TaskQueue` uses `heapq` with `QueueEntry(priority, deadline, sequence)` ordering.
- Deduplication uses a `set[str]` of seen task_ids; `nack` discards the id before re-enqueue to allow reprocessing.
- `TaskScheduler._eligible_workers` skips workers at max_concurrent or lacking capability.
- Affinity strategy falls back to least-loaded if preferred worker is not eligible.
- Zero-mock: real data only, `NotImplementedError` for unimplemented paths.

## Error Handling

- `TaskWorker.process_one` catches all `Exception` subclasses; returns `TaskResult(success=False, error=str(exc))`.
- `TaskScheduler.assign` returns empty string (not an exception) when no worker is available.
- `LockManager.acquire_all` raises `ValueError` for unregistered lock names.
- All errors logged before propagation.
