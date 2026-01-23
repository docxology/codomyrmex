# Codomyrmex Agents — src/codomyrmex/logistics

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Purpose

The Logistics module provides comprehensive workflow orchestration, task management, and scheduling capabilities for the Codomyrmex platform. It coordinates complex multi-module workflows, manages task queues with job execution, and supports advanced scheduling with cron expressions, recurring schedules, and timezone-aware execution. The module enables building DAG-based workflows, parallel task execution, resource allocation, and project-level orchestration.

## Active Components

### Orchestration Components

- `orchestration/` - Workflow and project orchestration
  - `project/` - Project-level orchestration components
    - Key Classes: `OrchestrationEngine`, `WorkflowManager`, `TaskOrchestrator`, `ProjectManager`, `ResourceManager`
    - Key Functions: `execute_workflow()`, `execute_task()`, `create_session()`
  - Key Data Classes: `OrchestrationSession`, `WorkflowStep`, `WorkflowExecution`

### Task Management

- `task/` - Task queue management and job execution
  - Key Classes: `JobScheduler`, `Queue`, `Job`
  - Key Functions: `start()`, `stop()`, `cancel_job()`, `get_job()`
  - `backends/` - Queue backend implementations
    - Key Classes: `InMemoryQueue`

### Scheduling Components

- `schedule/` - Advanced scheduling capabilities
  - Key Classes: `ScheduleManager`, `CronScheduler`, `CronExpression`, `RecurringScheduler`, `RecurringSchedule`, `TimezoneManager`
  - Key Functions: `schedule_cron()`, `schedule_recurring()`, `cancel()`, `list_tasks()`

## Key Classes and Functions

| Class/Function | Module | Purpose |
| :--- | :--- | :--- |
| `OrchestrationEngine` | orchestration | Main engine coordinating all orchestration components |
| `WorkflowManager` | orchestration | Creates, lists, and executes workflows |
| `TaskOrchestrator` | orchestration | Orchestrates individual task execution |
| `ProjectManager` | orchestration | Manages project-level workflow execution |
| `ResourceManager` | orchestration | Allocates and manages resources for sessions |
| `OrchestrationSession` | orchestration | Represents an orchestration session with tracking |
| `JobScheduler` | task | Executes scheduled jobs from the queue |
| `Queue` | task | Task queue with enqueue/dequeue operations |
| `Job` | task | Represents a scheduled job with status |
| `ScheduleManager` | schedule | Main scheduler interface for cron and recurring tasks |
| `CronScheduler` | schedule | Handles cron-based scheduling |
| `CronExpression` | schedule | Parses and evaluates cron expressions |
| `RecurringScheduler` | schedule | Handles recurring schedule patterns |
| `TimezoneManager` | schedule | Manages timezone-aware scheduling |
| `execute_workflow()` | OrchestrationEngine | Execute a workflow with resource management |
| `create_session()` | OrchestrationEngine | Create new orchestration session |
| `schedule_cron()` | ScheduleManager | Schedule task with cron expression |
| `get_system_status()` | OrchestrationEngine | Get comprehensive system status |

## Operating Contracts

1. **Logging**: All components use `logging_monitoring` for structured logging
2. **Session Management**: Long-running operations use `OrchestrationSession` for state tracking
3. **Resource Allocation**: Resources are allocated per session and cleaned up on session close
4. **Event System**: `OrchestrationEngine` emits events for session and workflow lifecycle
5. **MCP Compatibility**: Module exposes MCP-compatible tool specifications for orchestration
6. **Thread Safety**: Session management uses locks for concurrent access

## Integration Points

- **logging_monitoring** - All components log via centralized logger
- **performance** - Performance monitoring for workflow execution
- **model_context_protocol** - MCP tool specifications for orchestration
- **agents** - Coordinates agent task execution
- **coding** - Executes code-related tasks in workflows

## Signposting

### Document Hierarchy

- **Self**: [AGENTS.md](AGENTS.md)
- **Parent**: [src/codomyrmex/AGENTS.md](../AGENTS.md)
- **Project Root**: [../../../AGENTS.md](../../../AGENTS.md)

### Sibling Modules

| Module | AGENTS.md | Purpose |
| :--- | :--- | :--- |
| orchestrator | [../orchestrator/AGENTS.md](../orchestrator/AGENTS.md) | Workflow orchestration |
| agents | [../agents/AGENTS.md](../agents/AGENTS.md) | AI agent integrations |
| coding | [../coding/AGENTS.md](../coding/AGENTS.md) | Code execution |
| performance | [../performance/AGENTS.md](../performance/AGENTS.md) | Performance profiling |
| ci_cd_automation | [../ci_cd_automation/AGENTS.md](../ci_cd_automation/AGENTS.md) | CI/CD pipelines |

### Child Directories

| Directory | Purpose |
| :--- | :--- |
| orchestration/ | Workflow and project orchestration |
| orchestration/project/ | Project-level orchestration engine |
| task/ | Task queue and job management |
| task/backends/ | Queue backend implementations |
| schedule/ | Cron and recurring scheduling |

### Related Documentation

- [README.md](README.md) - User documentation
- [SPEC.md](SPEC.md) - Functional specification
- [API_SPECIFICATION.md](API_SPECIFICATION.md) - API documentation
