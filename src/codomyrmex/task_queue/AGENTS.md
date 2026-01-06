# Codomyrmex Agents — src/codomyrmex/queue

## Signposting
- **Parent**: [codomyrmex](../AGENTS.md)
- **Self**: [Queue Agents](AGENTS.md)
- **Children**:
    - None
- **Key Artifacts**:
    - [Functional Spec](SPEC.md)
    - [Human Readme](README.md)

**Version**: v0.1.0 | **Status**: Proposed | **Last Updated**: December 2025

## Purpose

Queue module providing task queue management, job scheduling, and async task execution for the Codomyrmex platform. This module integrates with `project_orchestration` for workflow task management.

The queue module serves as the queue layer, providing backend-agnostic queue interfaces with support for in-memory, Redis, and other queue backends.

## Module Overview

### Key Capabilities
- **Job Queuing**: Enqueue and dequeue jobs from queues
- **Job Scheduling**: Schedule jobs for future execution
- **Priority Queues**: Support priority-based job ordering
- **Retry Logic**: Automatic job retry on failure
- **Monitoring**: Queue statistics and job status tracking

### Key Features
- Backend-agnostic queue interface
- Support for multiple queue backends
- Priority-based job ordering
- Job scheduling and delayed execution
- Automatic retry on failure

## Function Signatures

### Queue Operations

```python
def enqueue(job: Job, priority: int = 0) -> str
```

Add a job to the queue.

**Parameters:**
- `job` (Job): Job to enqueue
- `priority` (int): Job priority (higher = more priority)

**Returns:** `str` - Job ID

```python
def dequeue() -> Optional[Job]
```

Remove and return the next job from the queue.

**Returns:** `Optional[Job]` - Next job if available, None if queue is empty

```python
def schedule(job: Job, when: datetime) -> str
```

Schedule a job for future execution.

**Parameters:**
- `job` (Job): Job to schedule
- `when` (datetime): When to execute the job

**Returns:** `str` - Scheduled job ID

```python
def get_status(job_id: str) -> JobStatus
```

Get the status of a job.

**Parameters:**
- `job_id` (str): Job identifier

**Returns:** `JobStatus` - Job status object

```python
def cancel(job_id: str) -> bool
```

Cancel a scheduled or queued job.

**Parameters:**
- `job_id` (str): Job identifier

**Returns:** `bool` - True if cancellation successful

### Queue Statistics

```python
def get_stats() -> QueueStats
```

Get queue statistics.

**Returns:** `QueueStats` - Statistics object with queue length, processing rate, etc.

### Job Management

```python
class Job:
    task: str
    args: dict
    kwargs: dict
    priority: int
    retries: int
    max_retries: int
```

Job data structure.

```python
class JobStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
```

Job status enumeration.

## Active Components

### Core Implementation
- `__init__.py` – Module initialization and public API exports
- `queue.py` – Base queue interface
- `job.py` – Job data structures
- `scheduler.py` – Job scheduler implementation
- `backends/` – Backend implementations
  - `in_memory_queue.py` – In-memory queue backend
  - `redis_queue.py` – Redis queue backend

### Documentation
- `README.md` – Module usage and overview
- `AGENTS.md` – This file: agent documentation
- `SPEC.md` – Functional specification

## Operating Contracts

### Universal Queue Protocols

All queue operations within the Codomyrmex platform must:

1. **Job Serialization** - All jobs must be serializable
2. **Error Handling** - Handle queue failures gracefully
3. **Retry Logic** - Implement retry logic for failed jobs
4. **Status Tracking** - Track job status throughout lifecycle
5. **Resource Cleanup** - Clean up completed/failed jobs

### Integration Guidelines

When integrating with other modules:

1. **Use Project Orchestration** - Integrate with workflow orchestration
2. **Performance Monitoring** - Track queue performance metrics
3. **Logging** - Log job execution via logging_monitoring
4. **Error Recovery** - Implement job retry and failure handling

## Navigation Links

- **Human Documentation**: [README.md](README.md)
- **Functional Specification**: [SPEC.md](SPEC.md)

### Module Documentation
- **Module Overview**: [README.md](README.md) - Complete module documentation

### Platform Navigation
- **Parent Directory**: [codomyrmex](../README.md) - Package overview
- **Project Root**: [README](../../../README.md) - Main project documentation
- **Related Modules**:
    - [project_orchestration](../project_orchestration/AGENTS.md) - Workflow orchestration
    - [performance](../performance/AGENTS.md) - Performance monitoring

