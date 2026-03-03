# Logistics Module

**Version**: v1.0.8 | **Status**: Active | **Last Updated**: March 2026

## Overview

The Logistics module provides workflow orchestration, task queue management, job scheduling, cron/recurring schedule support, timezone management, task routing, resource allocation, schedule optimization, and progress tracking. It coordinates complex multi-step operations with project management and resource planning capabilities.

## PAI Integration

| Algorithm Phase | Logistics Role |
|----------------|----------------|
| PLAN | Workflow creation, task scheduling, resource allocation |
| EXECUTE | Task queue processing, job execution, workflow step execution |
| OBSERVE | Progress tracking, resource usage monitoring |

## Key Exports

| Export | Type | Description |
|--------|------|-------------|
| `WorkflowManager` | class | Manages workflow definitions and execution |
| `TaskOrchestrator` | class | Orchestrates task execution and dependencies |
| `ProjectManager` | class | Project lifecycle management |
| `ResourceManager` | class | Resource allocation and usage tracking |
| `OrchestrationEngine` | class | Core orchestration execution engine |
| `OrchestrationSession` | class | Session management for orchestration operations |
| `Queue` | class | Task queue with priority support |
| `Job` | class | Executable job with metadata |
| `JobScheduler` | class | Job scheduling and dispatch |
| `ScheduleManager` | class | Unified schedule management |
| `CronScheduler` | class | Cron-expression-based scheduling |
| `CronExpression` | class | Cron expression parsing and matching |
| `RecurringScheduler` | class | Recurring schedule execution |
| `RecurringSchedule` | class | Recurring schedule definition |
| `TimezoneManager` | class | Timezone-aware scheduling |
| `routing` | submodule | Task routing algorithms |
| `optimization` | submodule | Schedule optimization |
| `resources` | submodule | Resource allocation management |
| `tracking` | submodule | Progress and status tracking |

## Quick Start

```python
from codomyrmex.logistics import WorkflowManager, Queue, Job, CronScheduler

# Create and manage workflows
wfm = WorkflowManager()

# Queue jobs
queue = Queue()
job = Job(name="data_export", func=lambda: print("Exporting..."))
queue.enqueue(job)

# Schedule with cron
scheduler = CronScheduler()
```

## Architecture

```
logistics/
  __init__.py          # Public API exports
  orchestration/       # Workflow and project orchestration
    project/           # ProjectManager, WorkflowManager, TaskOrchestrator, etc.
  task/                # Task queue management
    queue.py           # Queue class
    job.py             # Job class
    scheduler.py       # JobScheduler
    backends/          # Queue backend implementations
  schedule/            # Scheduling subsystem
    cron.py            # CronScheduler, CronExpression
    recurring.py       # RecurringScheduler, RecurringSchedule
    scheduler.py       # ScheduleManager
    timezone.py        # TimezoneManager
  routing/             # Task routing algorithms
  optimization/        # Schedule optimization
  resources/           # Resource allocation
  tracking/            # Progress and status tracking
```

## Testing

```bash
uv run pytest src/codomyrmex/tests/unit/logistics/ -v
```

## Navigation

- [AGENTS.md](AGENTS.md) -- Agent coordination documentation
- [SPEC.md](SPEC.md) -- Technical specification
- [Source Module](../../../../logistics/)
