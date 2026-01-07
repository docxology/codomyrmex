# Codomyrmex Agents — src/codomyrmex/logistics

## Signposting
- **Parent**: [codomyrmex](../AGENTS.md)
- **Self**: [Agents](AGENTS.md)
- **Children**:
    - [orchestration](orchestration/AGENTS.md)
    - [task](task/AGENTS.md)
    - [schedule](schedule/AGENTS.md)
- **Key Artifacts**:
    - [Functional Spec](SPEC.md)
    - [Human Readme](README.md)

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Purpose
Logistics module providing orchestration, task management, and scheduling capabilities for coordinating workflows, jobs, and time-based execution.

## Active Components
- `README.md` – Project file
- `SPEC.md` – Project file
- `__init__.py` – Module initialization
- `orchestration/` – Orchestration submodule
- `task/` – Task queue submodule
- `schedule/` – Scheduling submodule

## Key Classes and Functions

### Orchestration (from orchestration submodule)
- `WorkflowManager` – Manages workflow definitions and execution
- `TaskOrchestrator` – Coordinates individual tasks and dependencies
- `ProjectManager` – High-level project lifecycle management
- `ResourceManager` – Manages shared resources and dependencies
- `OrchestrationEngine` – Core orchestration engine
- `OrchestrationSession` – Orchestration session management

### Task (from task submodule)
- `Queue` – Queue for task management
- `Job` – Job data structure
- `JobScheduler` – Job scheduler for executing scheduled jobs

### Schedule (from schedule submodule)
- `ScheduleManager` – Main scheduler interface
- `CronScheduler` – Cron-like scheduling with pattern parsing
- `RecurringScheduler` – Recurring schedule definitions

## Operating Contracts
- Maintain alignment between code, documentation, and configured workflows.
- Ensure Model Context Protocol interfaces remain available for sibling agents.
- Record outcomes in shared telemetry and update TODO queues when necessary.

## Navigation Links
- **Human Documentation**: [README.md](README.md)
- **Functional Specification**: [SPEC.md](SPEC.md)
- **📁 Parent Directory**: [codomyrmex](../README.md) - Parent directory documentation
- **🏠 Project Root**: [README](../../../README.md) - Main project documentation

