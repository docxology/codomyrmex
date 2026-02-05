# Task

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

Task queue management for logistics operations. Provides job scheduling, queue management, and async task execution with pluggable backends.

## Key Exports

- **`Queue`** -- Task queue supporting configurable backends for job management
- **`Job`** -- Representation of a single job with status tracking
- **`JobStatus`** -- Enum of job lifecycle states
- **`JobScheduler`** -- Scheduler for deferred and recurring job execution
- **`get_queue()`** -- Factory function to obtain a Queue instance (supports "in_memory" and "redis" backends)

## Additional Classes

- **`QueueError`** -- Exception raised when queue operations fail (extends `CodomyrmexError`)

## Directory Contents

- `__init__.py` - Package exports, QueueError definition, and `get_queue()` factory
- `job.py` - Job and JobStatus definitions
- `queue.py` - Queue implementation with backend support
- `scheduler.py` - JobScheduler for deferred execution
- `backends/` - Pluggable queue backend implementations
- `py.typed` - PEP 561 type stub marker

## Navigation

- **Parent Module**: [logistics](../README.md)
- **Project Root**: [../../../../README.md](../../../../README.md)
