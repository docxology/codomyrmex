# logistics

## Signposting
- **Parent**: [codomyrmex](../README.md)
- **Children**:
    - [orchestration](orchestration/README.md)
    - [task](task/README.md)
    - [schedule](schedule/README.md)
- **Key Artifacts**:
    - [Agent Guide](AGENTS.md)
    - [Functional Spec](SPEC.md)

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Overview

The logistics module consolidates orchestration, task management, and scheduling capabilities for coordinating workflows, jobs, and time-based execution.

## Submodules

### orchestration
Workflow and project orchestration. Manages complex workflows involving multiple modules, task dependencies, and execution order.

### task
Task queue management and job execution. Provides backend-agnostic queue interface with support for priority queues, job retries, and scheduling.

### schedule
Advanced scheduling capabilities including cron-like patterns, recurring schedules, and timezone-aware scheduling.

## Directory Contents
- `orchestration/` – Orchestration submodule
- `task/` – Task queue submodule
- `schedule/` – Scheduling submodule
- `__init__.py` – Module initialization
- `README.md` – This file
- `AGENTS.md` – Technical documentation
- `SPEC.md` – Functional specification

## Navigation
- **Technical Documentation**: [AGENTS.md](AGENTS.md)
- **Functional Specification**: [SPEC.md](SPEC.md)
- **Parent Directory**: [codomyrmex](../README.md)
- **Project Root**: [README](../../../README.md)

## Getting Started

To use this module in your project, import the necessary components:

```python
from codomyrmex.logistics import (
    WorkflowManager,
    TaskOrchestrator,
    Queue,
    Job,
    ScheduleManager,
    CronScheduler,
)

# Workflow orchestration
workflow_mgr = WorkflowManager()
workflow = workflow_mgr.create_workflow("my_workflow")
workflow.add_step("step1", action=lambda: print("Step 1"))
workflow.add_step("step2", action=lambda: print("Step 2"), depends_on=["step1"])
workflow_mgr.execute(workflow)

# Task queue
queue = Queue()
job = Job(task="process_data", data={"file": "data.csv"})
queue.enqueue(job)
result = queue.dequeue()

# Scheduling with cron
scheduler = ScheduleManager()
cron = CronScheduler()
cron.schedule("0 9 * * *", lambda: print("Daily task at 9 AM"))
scheduler.start()
```

