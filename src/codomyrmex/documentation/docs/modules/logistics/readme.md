# Logistics Module

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

Comprehensive logistics module that consolidates orchestration, task management, and scheduling capabilities for the Codomyrmex platform. Provides workflow and project orchestration engines, job queue management, cron and recurring schedule support with timezone awareness, plus submodules for task routing algorithms, schedule optimization, resource allocation, and progress tracking.

## Installation

```bash
uv add codomyrmex
```

Or for development:

```bash
uv sync
```

## Key Exports

### Orchestration
- **`WorkflowManager`** -- Manages workflow definitions, DAG construction, and workflow lifecycle
- **`TaskOrchestrator`** -- Coordinates task execution order and dependency resolution across workflows
- **`ProjectManager`** -- Manages project-level orchestration including multi-workflow coordination
- **`ResourceManager`** -- Allocates and tracks resources across orchestrated tasks
- **`OrchestrationEngine`** -- Core engine that drives workflow execution with state management
- **`OrchestrationSession`** -- Represents an active orchestration execution session with context and history

### Task Management
- **`Queue`** -- Priority-based task queue with enqueue, dequeue, and peek operations
- **`Job`** -- Represents an executable unit of work with status, dependencies, and retry configuration
- **`JobScheduler`** -- Schedules and dispatches jobs from queues based on priority and resource availability

### Scheduling
- **`ScheduleManager`** -- Centralized manager for all schedule types (cron, recurring, one-off)
- **`CronScheduler`** -- Executes tasks on cron-style schedules
- **`CronExpression`** -- Parses and evaluates standard cron expressions (minute, hour, day, month, weekday)
- **`RecurringScheduler`** -- Manages interval-based recurring task execution
- **`RecurringSchedule`** -- Defines a recurring schedule with interval, start time, and end conditions
- **`TimezoneManager`** -- Handles timezone-aware scheduling and time conversions

### Submodules
- **`routing`** -- Task routing algorithms for distributing work across executors
- **`optimization`** -- Schedule optimization strategies for throughput and latency
- **`resources`** -- Resource pool management and capacity planning
- **`tracking`** -- Progress monitoring and status reporting for running workflows

## Directory Contents

- `orchestration/` -- Workflow management, project orchestration, and the core engine
- `task/` -- Job and queue implementations with scheduler
- `schedule/` -- Cron expressions, recurring schedules, and timezone management
- `routing/` -- Task routing algorithms
- `optimization/` -- Schedule and resource optimization
- `resources/` -- Resource allocation and pool management
- `tracking/` -- Progress and status tracking

## Quick Start

```python
import codomyrmex.logistics
```

## Testing

```bash
uv run python -m pytest src/codomyrmex/tests/ -k logistics -v
```

## Navigation

- **Full Documentation**: [docs/modules/logistics/](../../../docs/modules/logistics/)
- **Parent Directory**: [codomyrmex](../README.md)
- **Project Root**: ../../../README.md
