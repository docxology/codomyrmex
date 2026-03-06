# Concurrency Tasks

> **codomyrmex v1.1.4** | March 2026

## Overview

Distributed task management subsystem providing a priority queue with deduplication and dead-letter handling, a strategy-based task scheduler (round-robin, least-loaded, affinity), and an error-isolated task worker. Tasks flow through the queue, are assigned to workers by the scheduler, and produce `TaskResult` objects on completion.

## PAI Integration

| PAI Phase | Relevance | Usage |
|-----------|-----------|-------|
| EXECUTE | Primary | `TaskQueue` dispatches tasks; `TaskWorker` processes them |
| PLAN | Primary | `TaskScheduler` assigns tasks to workers using configurable strategies |
| OBSERVE | Supporting | `TaskQueue` properties (`pending_count`, `in_flight_count`, `dead_letter_count`) and `TaskWorker` counters for monitoring |

## Key Exports

| Name | Type | Source | Purpose |
|------|------|--------|---------|
| `Task` | dataclass | `task_queue.py` | Distributable task with ID, type, payload, priority, deadline, retries |
| `TaskPriority` | enum | `task_queue.py` | Priority levels: CRITICAL, HIGH, NORMAL, LOW, BACKGROUND |
| `TaskStatus` | enum | `task_queue.py` | Lifecycle: PENDING, IN_FLIGHT, COMPLETED, FAILED, DEAD_LETTER |
| `TaskQueue` | class | `task_queue.py` | Priority queue with deduplication, deadline expiry, dead-letter support |
| `TaskScheduler` | class | `task_scheduler.py` | Assigns tasks to workers via round-robin, least-loaded, or affinity strategies |
| `SchedulingStrategy` | enum | `task_scheduler.py` | Strategy selection: ROUND_ROBIN, LEAST_LOADED, AFFINITY |
| `WorkerInfo` | dataclass | `task_scheduler.py` | Worker metadata (capabilities, max_concurrent, current_load) |
| `TaskWorker` | class | `task_worker.py` | Processes tasks with error isolation and timeout |
| `TaskResult` | dataclass | `task_worker.py` | Processing result with success/failure, duration, and error details |

## Quick Start

```python
from codomyrmex.concurrency.tasks import (
    SchedulingStrategy,
    Task,
    TaskPriority,
    TaskQueue,
    TaskScheduler,
    TaskWorker,
)

# Set up queue and enqueue tasks
queue = TaskQueue(max_retries=3)
queue.enqueue(Task(task_type="analyze", priority=TaskPriority.HIGH, payload={"file": "main.py"}))
queue.enqueue(Task(task_type="lint", priority=TaskPriority.NORMAL))

# Set up scheduler with workers
scheduler = TaskScheduler(strategy=SchedulingStrategy.LEAST_LOADED)
scheduler.register_worker("w-1", capabilities=["analyze", "lint"], max_concurrent=5)
scheduler.register_worker("w-2", capabilities=["analyze"], max_concurrent=3)

# Process tasks
worker = TaskWorker(
    worker_id="w-1",
    handler=lambda task: {"processed": task.task_id},
)
worker.start()

task = queue.dequeue()
if task:
    assigned = scheduler.assign(task)
    result = worker.process_one(task)
    if result.success:
        queue.ack(task.task_id)
        scheduler.report_completion(assigned)
    else:
        queue.nack(task.task_id)  # Retry or dead-letter
```

## Architecture

```
concurrency/tasks/
    __init__.py            # Re-exports from all submodules
    task_queue.py           # TaskQueue, Task, TaskPriority, TaskStatus, QueueEntry
    task_scheduler.py       # TaskScheduler, SchedulingStrategy, WorkerInfo
    task_worker.py          # TaskWorker, TaskResult
```

## Testing

```bash
uv run pytest src/codomyrmex/tests/unit/concurrency/ -v -k task
```

## Navigation

- Parent: [concurrency](../README.md)
- AGENTS: [AGENTS.md](AGENTS.md)
- SPEC: [SPEC.md](SPEC.md)
- Project root: [codomyrmex](../../../../README.md)
