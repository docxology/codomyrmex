# Codomyrmex Agents — src/codomyrmex/logistics/task

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Purpose

Provides task queue management, job scheduling, and async task execution. This module handles job lifecycle management from creation through execution and result retrieval.

## Active Components

- `queue.py` - Queue abstraction with pluggable backends
- `job.py` - Job definition and status tracking
- `scheduler.py` - Job scheduling and execution coordination
- `backends/` - Queue backend implementations (in_memory, redis)
- `__init__.py` - Module exports with factory functions
- `SPEC.md` - Module specification
- `README.md` - Module documentation

## Key Classes and Functions

### queue.py
- **`Queue`** - Abstract queue interface for job management
  - `enqueue(job)` - Adds job to queue
  - `dequeue()` - Removes and returns next job
  - `peek()` - Views next job without removing
  - `size()` - Returns queue length
  - `clear()` - Empties the queue

### job.py
- **`Job`** - Represents an executable job unit
  - `job_id` - Unique identifier
  - `name` - Human-readable job name
  - `payload` - Job data/parameters
  - `priority` - Execution priority (higher = sooner)
  - `status` - Current JobStatus
  - `created_at`, `started_at`, `completed_at` - Timestamps
  - `result`, `error` - Execution outcomes
- **`JobStatus`** - Enum: PENDING, RUNNING, COMPLETED, FAILED, CANCELLED, RETRY

### scheduler.py
- **`JobScheduler`** - Coordinates job execution
  - `schedule(job, when)` - Schedules job for future execution
  - `run_now(job)` - Executes job immediately
  - `cancel(job_id)` - Cancels pending job
  - `get_status(job_id)` - Returns job status
  - `get_result(job_id)` - Returns completed job result

### Module Functions
- **`get_queue(backend)`** - Factory function returning Queue instance
  - `backend="in_memory"` - Default in-memory queue
  - `backend="redis"` - Redis-backed queue for persistence
- **`QueueError`** - Custom exception for queue operation failures

## Operating Contracts

- Jobs maintain unique IDs throughout lifecycle
- Priority determines dequeue order (higher priority first)
- Failed jobs can be retried based on retry policy
- Queue backends are interchangeable via factory function
- Job status transitions follow defined state machine

## Signposting

- **Dependencies**: Uses `logging_monitoring` for logging, `exceptions` for errors
- **Parent Directory**: [logistics](../README.md) - Parent module documentation
- **Related Modules**:
  - `backends/` - Backend implementations (in_memory_queue.py)
  - `schedule/` - Advanced scheduling patterns
  - `orchestration/` - Higher-level task orchestration
- **Project Root**: [../../../../README.md](../../../../README.md) - Main project documentation
