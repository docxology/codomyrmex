# task_queue

## Signposting
- **Parent**: [logistics](../README.md)
- **Children**:
    - [backends](backends/README.md)
- **Key Artifacts**:
    - [Agent Guide](AGENTS.md)
    - [Functional Spec](SPEC.md)

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Overview

Task queue management and job execution. Provides backend-agnostic queue interface with support for priority queues, job retries, and scheduling. Integrates with logistics.orchestration for workflow task management.

## Directory Contents
- `README.md` – File
- `SPEC.md` – File
- `__init__.py` – File
- `backends/` – Subdirectory
- `job.py` – File
- `queue.py` – File
- `scheduler.py` – File

## Navigation
- **Technical Documentation**: [AGENTS.md](AGENTS.md)
- **Functional Specification**: [SPEC.md](SPEC.md)
- **Parent Directory**: [logistics](../README.md)
- **Project Root**: [README](../../../../README.md)

## Getting Started

To use this module in your project, import the necessary components:

```python
from codomyrmex.logistics.task import Queue, Job, JobScheduler

# Create a queue
queue = Queue(backend="in_memory")

# Create a job
job = Job(task="my_task", args={}, kwargs={})

# Enqueue the job
job_id = queue.enqueue(job, priority=1)

# Create a scheduler
scheduler = JobScheduler(queue, check_interval=1)
scheduler.start()
```

