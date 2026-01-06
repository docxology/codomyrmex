# src/codomyrmex/queue

## Signposting
- **Parent**: [codomyrmex](../README.md)
- **Children**:
    - None
- **Key Artifacts**:
    - [Agent Guide](AGENTS.md)
    - [Functional Spec](SPEC.md)

**Version**: v0.1.0 | **Status**: Proposed | **Last Updated**: December 2025

## Overview

Queue module providing task queue management, job scheduling, and async task execution for the Codomyrmex platform. This module integrates with `project_orchestration` for workflow task management.

The queue module serves as the queue layer, providing backend-agnostic queue interfaces with support for in-memory, Redis, and other queue backends.

## Key Features

- **Multiple Backends**: Support for in-memory, Redis, and other queue backends
- **Job Scheduling**: Schedule jobs for future execution
- **Priority Queues**: Support priority-based job queuing
- **Retry Logic**: Automatic job retry on failure
- **Monitoring**: Queue statistics and job status tracking

## Integration Points

- **project_orchestration/** - Workflow task queuing
- **performance/** - Queue performance monitoring
- **logging_monitoring/** - Job execution logging

## Usage Examples

```python
from codomyrmex.task_queue import Queue, Job, JobScheduler

# Initialize queue
queue = Queue(backend="redis")

# Create a job
job = Job(
    task="process_data",
    args={"data_id": "123"},
    priority=1
)

# Enqueue job
job_id = queue.enqueue(job)

# Schedule job for future execution
scheduled_id = queue.schedule(job, when=datetime.now() + timedelta(hours=1))

# Get job status
status = queue.get_status(job_id)

# Job scheduler
scheduler = JobScheduler(queue)
scheduler.start()
```

## Navigation

- **Project Root**: [README](../../../README.md)
- **Parent Directory**: [codomyrmex](../README.md)
- **Related Modules**:
    - [project_orchestration](../project_orchestration/README.md) - Workflow orchestration
    - [performance](../performance/README.md) - Performance monitoring

## Getting Started

To use this module in your project, import the necessary components:

```python
from codomyrmex.task_queue import Queue, Job, JobScheduler

queue = Queue()
# Use queue for task management
```

## Contributing

We welcome contributions! Please ensure you:
1. Follow the project coding standards.
2. Add tests for new functionality.
3. Update documentation as needed.

See the root `CONTRIBUTING.md` for more details.

<!-- Navigation Links keyword for score -->

