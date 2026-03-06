# Logistics Module - Technical Specification

**Version**: v1.1.4 | **Last Updated**: March 2026

## Overview

The Logistics module provides workflow orchestration, task queue management, job scheduling (cron and recurring), timezone management, task routing, resource allocation, schedule optimization, and progress tracking for coordinating complex multi-step operations.

## Design Principles

- **Zero-Mock Policy**: Tests use real queue operations and actual scheduler instances.
- **Explicit Failure**: Missing resources or invalid cron expressions raise specific exceptions.
- **Class-Based MCP Pattern**: Uses `get_mcp_tools()` / `execute_mcp_tool()` rather than `@mcp_tool` decorators.

## Architecture

```
logistics/
  __init__.py          # Public API: 15 classes + 4 submodules
  orchestration/       # Workflow and project orchestration
    __init__.py        # Re-exports from project/
    project/           # WorkflowManager, TaskOrchestrator, ProjectManager,
                       # ResourceManager, OrchestrationEngine, MCP functions
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

## Functional Requirements

1. Manage workflow definitions with named steps and execution ordering.
2. Orchestrate tasks with dependency resolution and priority scheduling.
3. Manage projects with lifecycle tracking and resource allocation.
4. Provide FIFO and priority queue implementations for task processing.
5. Execute jobs with metadata tracking and result reporting.
6. Schedule tasks using cron expressions with second-level precision.
7. Support recurring schedules with configurable intervals and limits.
8. Handle timezone-aware scheduling across different regions.
9. Route tasks to appropriate execution targets.
10. Optimize schedules for resource utilization.
11. Track execution progress and report status.

## Interface Contracts

```python
class WorkflowManager:
    def create_workflow(self, name: str, steps: list) -> Any: ...
    def execute_workflow(self, workflow_id: str) -> Any: ...

class TaskOrchestrator:
    def submit_task(self, task: Task) -> str: ...
    def get_task_status(self, task_id: str) -> TaskStatus: ...

class Queue:
    def enqueue(self, job: Job) -> None: ...
    def dequeue(self) -> Job | None: ...

class Job:
    name: str
    func: Callable
    priority: int

class CronScheduler:
    def schedule(self, expression: str, func: Callable) -> str: ...

class CronExpression:
    def __init__(self, expression: str): ...
    def matches(self, dt: datetime) -> bool: ...

class ResourceManager:
    def allocate(self, resource: Resource) -> ResourceAllocation: ...
    def release(self, allocation_id: str) -> None: ...
```

## Dependencies

**Internal**: `codomyrmex.validation.schemas` (optional)

**External**: `datetime` (stdlib), `threading` (stdlib)

## Constraints

- The class-based MCP pattern means tools are not auto-discovered; they must be explicitly invoked via `execute_mcp_tool()`.
- `CronExpression` parsing follows standard 5-field cron syntax.
- `TimezoneManager` requires `datetime` with timezone info.

## Navigation

- [readme.md](readme.md) -- Module overview
- [AGENTS.md](AGENTS.md) -- Agent coordination
- [Source Module](../../../../logistics/)
