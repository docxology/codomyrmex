# Codomyrmex Agents — src/codomyrmex/task_queue

## Signposting
- **Parent**: [codomyrmex](../AGENTS.md)
- **Self**: [Agents](AGENTS.md)
- **Children**:
    - [backends](backends/AGENTS.md)
- **Key Artifacts**:
    - [Functional Spec](SPEC.md)
    - [Human Readme](README.md)

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Purpose
Queue implementation for task management. Provides job queuing, scheduling, and execution capabilities with multiple backend support.

## Active Components
- `README.md` – Project file
- `SPEC.md` – Project file
- `__init__.py` – Project file
- `backends/` – Directory containing backends components (in_memory, redis)
- `job.py` – Job data structures and status management
- `queue.py` – Queue implementation with backend abstraction
- `scheduler.py` – Job scheduler for executing scheduled jobs

## Key Classes and Functions

### Queue (`queue.py`)
- `Queue(backend: str = "in_memory")` – Initialize queue with specified backend
- `enqueue(job: Job, priority: int = 0) -> str` – Add a job to the queue, returns job ID
- `dequeue() -> Optional[Job]` – Remove and return the next job from the queue
- `schedule(job: Job, when: datetime) -> str` – Schedule a job for future execution
- `get_status(job_id: str) -> JobStatus` – Get the status of a job
- `cancel(job_id: str) -> bool` – Cancel a scheduled or queued job
- `size() -> int` – Get the number of jobs in the queue
- `clear() -> None` – Clear all jobs from the queue

### Job (`job.py`)
- `JobStatus` (Enum) – Job status enumeration (PENDING, RUNNING, COMPLETED, FAILED, CANCELLED)
- `Job` (dataclass) – Job data structure with fields:
  - `task: str` – Task identifier
  - `args: dict` – Task arguments
  - `kwargs: dict` – Task keyword arguments
  - `priority: int` – Job priority (higher = more priority)
  - `retries: int` – Number of retry attempts
  - `max_retries: int` – Maximum retry attempts
  - `job_id: Optional[str]` – Unique job identifier
  - `status: JobStatus` – Current job status
  - `created_at: Optional[datetime]` – Job creation timestamp
  - `scheduled_for: Optional[datetime]` – Scheduled execution time

### JobScheduler (`scheduler.py`)
- `JobScheduler(queue: Queue, check_interval: int = 1)` – Initialize job scheduler
- `start() -> None` – Start the scheduler in a background thread
- `stop() -> None` – Stop the scheduler
- `_run() -> None` – Internal scheduler loop (runs in background thread)

## Operating Contracts
- Maintain alignment between code, documentation, and configured workflows.
- Ensure Model Context Protocol interfaces remain available for sibling agents.
- Record outcomes in shared telemetry and update TODO queues when necessary.

## Navigation Links
- **Human Documentation**: [README.md](README.md)
- **Functional Specification**: [SPEC.md](SPEC.md)
- **📁 Parent Directory**: [codomyrmex](../README.md) - Parent directory documentation
- **🏠 Project Root**: [README](../../../README.md) - Main project documentation