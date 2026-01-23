# Codomyrmex Agents — src/codomyrmex/logistics/task/backends

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Purpose

Implements queue backend strategies for the task module. Backends provide the underlying storage and retrieval mechanisms for job queues, supporting both in-memory (development/testing) and persistent (production) configurations.

## Active Components

- `in_memory_queue.py` - In-memory queue implementation using Python heap
- `__init__.py` - Backend module initialization
- `SPEC.md` - Directory specification
- `README.md` - Directory documentation

## Key Classes and Functions

### in_memory_queue.py
- **`InMemoryQueue`** - Heap-based in-memory queue implementation
  - `__init__()` - Initializes empty priority queue, job registry, and scheduled list
  - `enqueue(job)` - Adds job to priority queue (uses negative priority for max-heap behavior)
  - `dequeue()` - Returns highest-priority job, checking scheduled jobs first
  - `schedule(job, when)` - Schedules job for future execution at specified datetime
  - `get_status(job_id)` - Returns status of tracked job
  - `cancel(job_id)` - Cancels queued or scheduled job, removes from all structures
  - `get_stats()` - Returns queue statistics (queue_length, scheduled_count, total_jobs)

### Internal Data Structures
```python
_queue: list[tuple]  # Priority queue: (-priority, timestamp, job)
_jobs: dict[str, Job]  # Job ID to Job mapping for status lookups
_scheduled: list[tuple[datetime, Job]]  # Scheduled jobs sorted by time
```

### Dequeue Behavior
1. Check scheduled jobs for any ready to execute (datetime <= now)
2. Move ready scheduled jobs to main queue
3. Pop highest-priority job from queue
4. Update job status to RUNNING
5. Return job for execution

## Operating Contracts

- Jobs ordered by priority (higher priority dequeued first)
- Scheduled jobs automatically promoted when their time arrives
- Job status updated to RUNNING upon dequeue
- Cancelled jobs removed from both queue and scheduled list
- Queue is not persistent (data lost on process restart)
- Thread-safety not guaranteed (use external synchronization if needed)

## Signposting

- **Dependencies**: Uses `heapq` for priority queue, `job.py` for Job class
- **Parent Directory**: [task](../README.md) - Parent module documentation
- **Related Modules**:
  - `../job.py` - Job and JobStatus definitions
  - `../queue.py` - Abstract Queue interface
  - `../scheduler.py` - JobScheduler using backends
- **Project Root**: [../../../../../README.md](../../../../../README.md) - Main project documentation
