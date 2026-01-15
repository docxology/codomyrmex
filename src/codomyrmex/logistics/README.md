# Logistics Module

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Overview

The Logistics module provides orchestration, task management, and scheduling capabilities for Codomyrmex, coordinating workflows, jobs, and time-based execution.

## Submodules

| Submodule | Description |
|-----------|-------------|
| `orchestration/` | Workflow and project orchestration |
| `task/` | Task queue management and job execution |
| `schedule/` | Advanced scheduling with cron and timezone support |

## Key Features

- **Workflow Orchestration**: Define and execute multi-step workflows
- **Task Queue**: Job queuing with priority and dependencies
- **Cron Scheduling**: Unix-style cron expression support
- **Recurring Schedules**: Interval-based recurring tasks
- **Timezone Support**: Timezone-aware scheduling
- **Resource Management**: Track and allocate resources

## Quick Start

```python
from codomyrmex.logistics import (
    # Orchestration
    WorkflowManager, TaskOrchestrator, OrchestrationEngine,
    # Task
    Queue, Job, JobScheduler,
    # Schedule
    ScheduleManager, CronScheduler, CronExpression,
    RecurringScheduler, RecurringSchedule,
)

# Workflow Orchestration
workflow_manager = WorkflowManager()
workflow = workflow_manager.create("data_pipeline")
workflow.add_step("extract", extract_data)
workflow.add_step("transform", transform_data, depends_on=["extract"])
workflow.add_step("load", load_data, depends_on=["transform"])
workflow.execute()

# Task Queue
queue = Queue(name="background_jobs")
job = Job(target=process_file, args=("input.csv",))
queue.enqueue(job)
queue.process()

# Cron Scheduling
scheduler = CronScheduler()
scheduler.schedule(
    CronExpression("0 9 * * 1-5"),  # 9 AM weekdays
    target=daily_report
)
scheduler.start()

# Recurring Schedule
recurring = RecurringScheduler()
recurring.every(hours=1).do(healthcheck)
```

## Core Classes

### Orchestration
| Class | Description |
|-------|-------------|
| `WorkflowManager` | Create and manage workflows |
| `TaskOrchestrator` | Coordinate task execution |
| `ProjectManager` | Manage project resources |
| `OrchestrationEngine` | Core engine for orchestration |
| `OrchestrationSession` | Session state for orchestration |
| `ResourceManager` | Track and allocate resources |

### Task
| Class | Description |
|-------|-------------|
| `Queue` | Task queue with FIFO/priority modes |
| `Job` | Individual job with target and args |
| `JobScheduler` | Schedule jobs for execution |

### Schedule
| Class | Description |
|-------|-------------|
| `ScheduleManager` | Central schedule management |
| `CronScheduler` | Cron-based scheduling |
| `CronExpression` | Parse and evaluate cron expressions |
| `RecurringScheduler` | Interval-based scheduling |
| `RecurringSchedule` | Define recurring intervals |
| `TimezoneManager` | Timezone conversions |

## Navigation

- **Technical Documentation**: [AGENTS.md](AGENTS.md)
- **Functional Specification**: [SPEC.md](SPEC.md)
- **Parent Directory**: [codomyrmex](../README.md)
- **Project Root**: [README](../../../README.md)
