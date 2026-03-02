# Orchestration Project -- Functional Specification

## Overview

Core implementation of the Codomyrmex orchestration system. Coordinates workflows, tasks, resources, and project lifecycles via DAG-based execution with parallel processing support.

## Architecture

All classes are instantiated as lazy singletons via module-level `get_*()` factory functions exported from `__init__.py`.

```
project/
  orchestration_engine.py    # OrchestrationEngine (sessions, health, events)
  workflow_manager.py        # WorkflowManager (CRUD, JSON config, DAG, parallel)
  task_orchestrator.py       # TaskOrchestrator (priority queues, background worker)
  resource_manager.py        # ResourceManager (capacity allocation, thread-safe)
  parallel_executor.py       # ParallelExecutor (ThreadPoolExecutor, dependency mgmt)
  workflow_dag.py            # WorkflowDAG (validation, cycle detection, topo sort)
  project_manager.py         # ProjectManager (lifecycle, scaffolding, docs)
  documentation_generator.py # DocumentationGenerator (template-based RASP gen)
  mcp_tools.py               # OrchestrationMCPTools (class-based, 10 tools)
```

## Key Classes

### `OrchestrationEngine`

| Field / Method | Description |
|----------------|-------------|
| `sessions: dict[str, OrchestrationSession]` | Active sessions keyed by ID |
| `_lock: threading.RLock` | Guards session state for concurrent access |
| `create_session(name, mode)` | Create session; returns `OrchestrationSession` |
| `execute_workflow(name, params, session_id)` | Delegate to `WorkflowManager` within a session context |
| `submit_task(task)` | Submit `Task` to internal `TaskOrchestrator` |
| `get_health_status()` | Component health, uptime, error counts |
| `get_system_status()` | Aggregate status across all subsystems |
| `register_event_handler(event_type, handler)` | Register `Callable` for orchestration events |

Modes: `OrchestrationMode.SEQUENTIAL | PARALLEL | PRIORITY | RESOURCE_AWARE`.

### `WorkflowManager`

| Field / Method | Description |
|----------------|-------------|
| `workflows: dict[str, list[WorkflowStep]]` | Registered workflow definitions |
| `config_dir: Path` | Directory for JSON workflow files (default: `config/workflows/production`) |
| `create_workflow(name, steps)` | Register workflow; overwrites if exists |
| `execute_workflow(name, **params)` | Submit steps as tasks via `TaskOrchestrator`; returns `WorkflowExecution` |
| `create_workflow_dag(tasks)` | Build `WorkflowDAG` from task dicts |
| `execute_parallel_workflow(workflow)` | Run via `ParallelExecutor`; returns status dict with task results |
| `validate_workflow_dependencies(tasks)` | Return list of dependency validation errors |
| `get_workflow_execution_order(tasks)` | Topological sort into parallelisable levels |

### `TaskOrchestrator`

| Field / Method | Description |
|----------------|-------------|
| `_queues: dict[TaskPriority, deque]` | Per-priority task queues (CRITICAL=0 through BACKGROUND=4) |
| `submit_task(task)` | Enqueue by priority; returns task ID |
| `get_task_status(task_id)` | Return `TaskStatus` |
| `cancel_task(task_id)` | Cancel pending or running task |
| `start_background_processing()` | Start daemon `Thread` consuming from priority queues |

Background worker checks: (1) dependency satisfaction, (2) resource availability via `ResourceManager`, (3) retry count vs `max_retries`.

### `ResourceManager`

| Field / Method | Description |
|----------------|-------------|
| `_resources: dict` | Registered resources with capacity and limits |
| `_lock: threading.Lock` | Thread-safe allocation guard |
| `register_resource(id, type, capacity, limits)` | Register resource with `ResourceLimits` |
| `allocate(resource_id, requester_id, amount)` | Allocate; returns `ResourceAllocation` or raises on insufficient capacity |
| `release(allocation_id)` | Release allocation, restore capacity |
| `get_usage(resource_id)` | Return `ResourceUsage` (current, peak, available) |

### `WorkflowDAG`

| Field / Method | Description |
|----------------|-------------|
| `tasks: dict[str, DAGTask]` | Tasks keyed by name |
| `validate()` | Check missing deps + DFS cycle detection |
| `topological_sort()` | Kahn's algorithm; returns ordered task names |
| `get_execution_levels()` | Group into parallelisable tiers |
| `to_mermaid()` | Mermaid flowchart string |

Raises `CycleDetectedError` (subclass of `DAGValidationError`).

### `ParallelExecutor`

Context manager wrapping `ThreadPoolExecutor`. `execute_tasks(tasks, dependencies)` resolves execution order and returns `dict[str, ExecutionResult]`. Supports configurable `max_workers` and per-task timeouts.

### `ProjectManager`

| Field / Method | Description |
|----------------|-------------|
| `create_project(name, type, description)` | Scaffold `src/`, `tests/`, `config/`, `docs/` dirs; generate RASP docs |
| `get_project(name)` | Lookup by name |
| `list_projects()` | Return all active `Project` instances |
| `update_project_status(name, status)` | Transition lifecycle status |

7 project types: `AI_ANALYSIS`, `WEB_APPLICATION`, `DATA_PIPELINE`, `ML_MODEL`, `DOCUMENTATION`, `RESEARCH`, `CUSTOM`.

## Dependencies

- `codomyrmex.logging_monitoring.core.logger_config` -- structured logging
- `codomyrmex.performance` -- optional `monitor_performance` decorator
- `codomyrmex.model_context_protocol` -- `MCPToolResult`, `MCPErrorDetail` (required for MCP tools)
- `jsonschema` -- not used directly here (used by config_management)
- Standard library: `threading`, `concurrent.futures`, `collections`, `uuid`, `json`, `pathlib`

## Error Handling

- `DAGValidationError` / `CycleDetectedError` -- DAG structural errors
- `ValueError` -- workflow not found, unknown task
- `RuntimeError` -- MCP unavailable (zero-mock enforcement)

## Navigation

- **Specification**: This file
- **Agent coordination**: [AGENTS.md](AGENTS.md)
- **Parent**: [orchestration/](../SPEC.md)
