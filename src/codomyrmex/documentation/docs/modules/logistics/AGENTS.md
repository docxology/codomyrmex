# Logistics Module - Agent Coordination

**Version**: v1.1.0 | **Last Updated**: March 2026

## Overview

The Logistics module provides agents with workflow orchestration, task queue management, job scheduling, cron/recurring support, and resource allocation. It uses a class-based MCP pattern (not `@mcp_tool` decorators) for tool exposure via the orchestration submodule.

## Key Files

| File | Class/Function | Role |
|------|---------------|------|
| `orchestration/project/` | `WorkflowManager` | Workflow definition and execution management |
| `orchestration/project/` | `TaskOrchestrator` | Task execution and dependency coordination |
| `orchestration/project/` | `ProjectManager` | Project lifecycle management |
| `orchestration/project/` | `ResourceManager` | Resource allocation and usage tracking |
| `orchestration/project/` | `OrchestrationEngine` | Core orchestration execution engine |
| `task/queue.py` | `Queue` | Priority task queue |
| `task/job.py` | `Job` | Executable job definition |
| `task/scheduler.py` | `JobScheduler` | Job scheduling and dispatch |
| `schedule/cron.py` | `CronScheduler`, `CronExpression` | Cron-based scheduling |
| `schedule/recurring.py` | `RecurringScheduler`, `RecurringSchedule` | Recurring schedule definitions |
| `schedule/timezone.py` | `TimezoneManager` | Timezone-aware scheduling |

## MCP Tools Available

The logistics module uses a class-based MCP pattern via `get_mcp_tools()`, `get_mcp_tool_definitions()`, and `execute_mcp_tool()` in the `orchestration` submodule. These are not auto-discovered by the `@mcp_tool` decorator system.

## Agent Instructions

1. Use `WorkflowManager` to define and manage multi-step workflows.
2. Use `TaskOrchestrator` to coordinate task execution with dependency management.
3. Use `Queue` and `Job` for asynchronous task processing.
4. Use `CronScheduler` for time-based recurring task scheduling.
5. Access MCP tools via `execute_mcp_tool()` from the orchestration submodule rather than the standard MCP bridge.

## Operating Contracts

- The orchestration submodule exposes factory functions: `get_workflow_manager()`, `get_task_orchestrator()`, `get_project_manager()`, `get_resource_manager()`, `get_orchestration_engine()`.
- `execute_workflow()` and `execute_task()` are convenience functions for direct execution.
- `cli_commands()` returns two CLI commands: `routes` (list submodules) and `status` (component availability).

## Common Patterns

```python
from codomyrmex.logistics import WorkflowManager, Queue, Job, CronScheduler
from codomyrmex.logistics.orchestration import get_workflow_manager, execute_task

# Factory pattern
wfm = get_workflow_manager()

# Direct queue usage
queue = Queue()
job = Job(name="task_1", func=lambda: "result")
queue.enqueue(job)

# Cron scheduling
cron = CronScheduler()
```

## PAI Agent Role Access Matrix

| Agent | Access Level | Primary Tools |
|-------|-------------|---------------|
| Engineer | Full | `WorkflowManager`, `TaskOrchestrator`, `Queue`, `JobScheduler` |
| Architect | Plan | `WorkflowManager`, `ResourceManager`, `ProjectManager` |
| QATester | Execute | `Queue`, `Job`, `execute_task` |

## Navigation

- [readme.md](readme.md) -- Module overview
- [SPEC.md](SPEC.md) -- Technical specification
- [Source Module](../../../../logistics/)
