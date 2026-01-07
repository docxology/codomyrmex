# backends

## Signposting
- **Parent**: [task](../README.md)
- **Children**:
    - None
- **Key Artifacts**:
    - [Agent Guide](AGENTS.md)
    - [Functional Spec](SPEC.md)

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Overview

Task queue backend implementations. Provides pluggable queue backends including in-memory queue for development and testing. Supports backend-agnostic queue interface for different storage requirements.

## Directory Contents
- `__init__.py` – File
- `in_memory_queue.py` – File

## Navigation
- **Technical Documentation**: [AGENTS.md](AGENTS.md)
- **Functional Specification**: [SPEC.md](SPEC.md)
- **Parent Directory**: [task](../README.md)
- **Project Root**: [README](../../../../../README.md)

## Getting Started

To use this module in your project, import the necessary components:

```python
from codomyrmex.logistics.task.backends import InMemoryQueue
from codomyrmex.logistics.task import Job

# Create an in-memory queue backend
queue = InMemoryQueue()

# Create and enqueue a job
job = Job(task="process_data", args={"file": "data.csv"}, kwargs={})
job_id = queue.enqueue(job)

# Dequeue the job
next_job = queue.dequeue()
```

