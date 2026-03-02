# Logistics Orchestration -- Functional Specification

## Overview

Orchestration subpackage coordinating workflows, tasks, resources, and project lifecycles. The `orchestration/` directory is a facade; all implementation lives in `project/`.

## Architecture

```
orchestration/
  __init__.py          # Re-exports ~40 symbols from project/
  project/
    orchestration_engine.py   # Central coordinator (sessions, health, metrics)
    workflow_manager.py       # Workflow CRUD + JSON config loading + DAG + parallel
    task_orchestrator.py      # Priority queue scheduler with background worker
    resource_manager.py       # Thread-safe capacity-based resource allocation
    parallel_executor.py      # ThreadPoolExecutor parallel task runner
    workflow_dag.py           # DAG validation, cycle detection, topological sort
    project_manager.py        # Project lifecycle + directory scaffolding
    documentation_generator.py # Template-based RASP doc generation
    mcp_tools.py              # Class-based MCP tool definitions (10 tools)
```

## Key Classes

### `OrchestrationEngine` (`orchestration_engine.py`)

Central coordinator managing sessions, workflows, tasks, and resources.

| Method | Description |
|--------|-------------|
| `create_session(name, mode)` | Create an `OrchestrationSession` (thread-safe via `RLock`) |
| `execute_workflow(name, params, session_id)` | Run a named workflow within a session |
| `submit_task(task)` | Submit a `Task` to the internal `TaskOrchestrator` |
| `get_health_status()` | Return system health including component states and metrics |
| `get_system_status()` | Aggregate status across all subsystems |
| `register_event_handler(event_type, handler)` | Register callback for orchestration events |

Execution modes: `SEQUENTIAL`, `PARALLEL`, `PRIORITY`, `RESOURCE_AWARE`.

### `WorkflowManager` (`workflow_manager.py`)

| Method | Description |
|--------|-------------|
| `create_workflow(name, steps)` | Register a workflow from `WorkflowStep` list |
| `execute_workflow(name, **params)` | Execute a workflow, returning `WorkflowExecution` |
| `create_workflow_dag(tasks)` | Build a `WorkflowDAG` from task dicts |
| `execute_parallel_workflow(workflow)` | Run tasks via `ParallelExecutor` with dependency ordering |
| `validate_workflow_dependencies(tasks)` | Return list of dependency errors |
| `get_workflow_execution_order(tasks)` | Topological sort into parallelisable levels |

Loads workflow JSON definitions from `config/workflows/production/*.json` on init.

### `TaskOrchestrator` (`task_orchestrator.py`)

| Method | Description |
|--------|-------------|
| `submit_task(task)` | Enqueue task by priority (5 levels: CRITICAL to BACKGROUND) |
| `get_task_status(task_id)` | Return current `TaskStatus` |
| `cancel_task(task_id)` | Cancel a pending or running task |
| `start_background_processing()` | Launch daemon thread for queue consumption |

Uses `collections.deque` per priority level. Background thread checks dependency satisfaction and resource availability before execution via `ThreadPoolExecutor`.

### `ResourceManager` (`resource_manager.py`)

| Method | Description |
|--------|-------------|
| `register_resource(resource_id, type, capacity)` | Register a resource with capacity limits |
| `allocate(resource_id, requester_id, amount)` | Allocate capacity (thread-safe via `Lock`) |
| `release(allocation_id)` | Release a prior allocation |
| `get_usage(resource_id)` | Return `ResourceUsage` with current/peak/available |

11 resource types: COMPUTE, MEMORY, STORAGE, NETWORK, API_QUOTA, DATABASE, CUSTOM, FILE_HANDLE, THREAD, PROCESS, LOCK.

### `WorkflowDAG` (`workflow_dag.py`)

| Method | Description |
|--------|-------------|
| `validate()` | Check for missing dependencies and cycles (DFS) |
| `topological_sort()` | Kahn's algorithm returning execution order |
| `get_execution_levels()` | Group tasks into parallelisable tiers |
| `to_mermaid()` | Generate Mermaid diagram string |

Raises `CycleDetectedError` (subclass of `DAGValidationError`) when cycles are found.

### `ParallelExecutor` (`parallel_executor.py`)

Context-manager-compatible executor using `ThreadPoolExecutor`. Accepts task lists with dependency dicts, resolves execution order, and returns `dict[str, ExecutionResult]` keyed by task name.

## Dependencies

- `codomyrmex.logging_monitoring` -- structured logging
- `codomyrmex.performance` -- optional performance monitoring
- `codomyrmex.model_context_protocol` -- MCP types (`MCPToolResult`, `MCPErrorDetail`)
- `codomyrmex.exceptions` -- error context creation
- Standard library: `threading`, `concurrent.futures`, `collections`, `uuid`, `json`

## Constraints

- Workflow JSON files must live in `config/workflows/production/` to be auto-loaded.
- `OrchestrationMCPTools` requires `codomyrmex.model_context_protocol` at import time; raises `RuntimeError` otherwise (zero-mock policy).
- DAG tasks must have unique names within a workflow.

## Navigation

- **Specification**: This file
- **Agent coordination**: [AGENTS.md](AGENTS.md)
- **Parent**: [logistics/](../SPEC.md)
