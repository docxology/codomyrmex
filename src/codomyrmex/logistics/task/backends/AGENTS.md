# Codomyrmex Agents — src/codomyrmex/logistics/task/backends

## Signposting
- **Parent**: [task](../AGENTS.md)
- **Self**: [Agents](AGENTS.md)
- **Children**:
    - None
- **Key Artifacts**:
    - [Functional Spec](SPEC.md)
    - [Human Readme](README.md)

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Purpose
Task queue backend implementations. Provides pluggable queue backends including in-memory queue for development and testing. Supports backend-agnostic queue interface for different storage requirements.

## Active Components
- `__init__.py` – Module exports and public API
- `in_memory_queue.py` – In-memory queue backend implementation

## Key Classes and Functions

### InMemoryQueue (`in_memory_queue.py`)
- `InMemoryQueue()` – In-memory queue backend
- `enqueue(job: Job) -> str` – Add job to queue
- `dequeue() -> Optional[Job]` – Remove and return next job
- `get_queue_size() -> int` – Get queue size
- `clear() -> None` – Clear all jobs from queue

## Operating Contracts
- Maintain alignment between code, documentation, and configured workflows.
- Ensure Model Context Protocol interfaces remain available for sibling agents.
- Record outcomes in shared telemetry and update TODO queues when necessary.

## Navigation Links
- **Human Documentation**: [README.md](README.md)
- **Functional Specification**: [SPEC.md](SPEC.md)
- **📁 Parent Directory**: [task](../README.md) - Parent directory documentation
- **🏠 Project Root**: [README](../../../../../README.md) - Main project documentation