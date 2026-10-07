# Orchestration Project -- Functional Specification

**Version**: v1.3.0 | **Status**: Active | **Last Updated**: October 2026

## Overview

Core implementation of the Codomyrmex orchestration system. Coordinates workflows, tasks, resources, and project lifecycles via DAG-based execution with parallel processing support.

## Architecture

All classes are instantiated as lazy singletons via module-level `get_*()` factory functions exported from `__init__.py`. The global engine returned by `get_orchestration_engine()` is built on the other global singletons, so workflows, tasks, projects and resources registered through `get_workflow_manager()`, `get_task_orchestrator()`, `get_project_manager()` and `get_resource_manager()` are the ones it uses.

```text
project/
  orchestration_engine.py    # OrchestrationEngine (sessions, health, events)
  workflow_manager.py        # WorkflowManager (CRUD, JSON config, DAG, parallel)
  task_orchestrator.py       # TaskOrchestrator (priority queues, dispatch, resources)
  resource_manager.py        # ResourceManager (capacity allocation, thread-safe)
  parallel_executor.py       # ParallelExecutor (ThreadPoolExecutor, dependency mgmt)
  workflow_dag.py            # WorkflowDAG (validation, cycle detection, topo sort)
  project_manager.py         # ProjectManager (lifecycle, scaffolding, docs)
  documentation_generator.py # DocumentationGenerator (template-based RASP gen)
  mcp_tools.py               # OrchestrationMCPTools (class-based, 10 tools)
```

## Task Dispatch

A task (or workflow step) names the code it runs with `module` and `action`, and is called as `action(**parameters)`:

1. A callable registered with `TaskOrchestrator.register_action(module, action, func)` (an `ActionRegistry` entry) is used first.
2. Otherwise `codomyrmex.<module>` is imported and its public attribute `<action>` is called. `module` may be dotted (`"coding.static_analysis"`); `action` must be a public name.
3. A coroutine function's result is run to completion in the worker thread.

An unknown module or action, a malformed name, or an exception raised by the callable marks the task `FAILED` with the error recorded on its `TaskResult`. Nothing is reported as completed unless the callable ran and returned. `ParallelExecutor` uses the same dispatch.

## Key Classes

### `OrchestrationEngine`

| Field / Method | Description |
| --- | --- |
| `OrchestrationEngine(config=None, *, workflow_manager=None, task_orchestrator=None, project_manager=None, resource_manager=None)` | Missing components are created from `config` (`workflows_dir`, `projects_dir`, `max_workers`) and wired together; `shutdown()` stops only an orchestrator the engine created |
| `create_session(user_id="system", **kwargs)` | Create session; returns the session ID |
| `execute_workflow(workflow_name, session_id=None, **params)` | Run a registered workflow synchronously; returns `success`, `status`, `execution_id`, `result` (per-step task results), `error`, `execution_time`, `steps_executed` |
| `execute_task(task, session_id=None)` | Submit a `Task` (or dict) and wait for it; unknown dependency IDs fail fast; the session's `timeout_seconds` cancels a task that does not finish |
| `execute_complex_workflow(definition, session_id=None)` | Run an ad-hoc `{"steps": [...], "dependencies": {...}}` definition with the same semantics as `WorkflowManager.execute_steps`; `success` is True only if every step completed |
| `execute_project_workflow(project_name, workflow_name, session_id=None, **params)` | Run a workflow for a registered project and record the run in the project's `metrics` |
| `create_project_from_workflow(project_name, workflow_name, template_name="ai_analysis", description="", session_id=None, **params)` | Create a project (`template_name` is a `ProjectType` value), run the workflow, add a `workflow_<name>_completed` milestone on success; `success` mirrors the workflow |
| `get_system_status()` / `get_metrics()` | Aggregate real component state (`get_execution_stats`, `get_projects_summary`, `get_resource_usage`, `get_performance_summary`) |
| `health_check()` | Component health summary |
| `register_event_handler(event, handler)` | Register `Callable` for orchestration events (`session_created`, `session_closed`, `workflow_completed`) |

Modes: `OrchestrationMode.SEQUENTIAL | PARALLEL | PRIORITY | RESOURCE_AWARE`.

### `WorkflowManager`

| Field / Method | Description |
| --- | --- |
| `workflows: dict[str, list[WorkflowStep]]` | Registered workflow definitions |
| `config_dir: Path` | Directory for JSON workflow files (default: `config/workflows/production`) |
| `task_orchestrator` | Orchestrator that runs steps (constructor argument; defaults to the global one) |
| `create_workflow(name, steps)` | Register workflow; overwrites if exists |
| `execute_workflow(name, **params)` | Synchronous; `params` are merged over every step's `parameters`. See `execute_steps`. Raises `ValueError` for an unknown workflow |
| `execute_steps(name, steps, params=None, timeout=None)` | Validate, submit steps in topological order (listing order is irrelevant), wait, and return a finished `WorkflowExecution` |
| `create_workflow_dag(tasks)` | Build `WorkflowDAG` from task dicts |
| `execute_parallel_workflow(workflow)` | Run via `ParallelExecutor` (sharing the orchestrator's registered actions); returns status dict with task results |
| `validate_workflow_dependencies(tasks)` | Return list of dependency validation errors |
| `get_workflow_execution_order(tasks)` | Topological sort into parallelisable levels |
| `get_performance_summary()` | Execution counts (total, successful, failed, running) and average duration |

`execute_steps` semantics:

- Missing dependencies, cycles and duplicate step names raise `ValueError` before anything runs; a step with `run_if` raises `NotImplementedError` (conditions are not supported).
- Independent steps run concurrently; a step whose dependency failed is failed without running; unrelated steps still run.
- The execution ends `COMPLETED` when every `required` step completed, otherwise `FAILED` with `error` listing each failed step. `end_time` and `step_results` (step name to task result dict) are always set.
- When `timeout` expires, unfinished steps are cancelled and the execution fails.

### `TaskOrchestrator`

| Field / Method | Description |
| --- | --- |
| `TaskOrchestrator(max_workers=4, resource_manager=None, actions=None)` | Defaults to the global `ResourceManager` and a new `ActionRegistry` |
| `queues: dict[TaskPriority, deque]` | Per-priority task queues (CRITICAL=0 through BACKGROUND=4) |
| `register_action(module, action, func)` | Register an explicit implementation for `module`/`action` |
| `submit_task(task)` | Enqueue by priority (or block on dependencies); returns task ID |
| `execute_task(task)` | Submit and block until the task finishes; returns its `TaskResult` |
| `wait_for_tasks(task_ids, timeout=None)` | Block until the given tasks finish; False on timeout; raises if processing was stopped while tasks are still queued |
| `cancel_task(task_id)` | A queued/blocked task never runs; a running task is marked cancelled and its late result discarded |
| `start_processing()` / `stop_execution()` | Start / stop the background worker thread |
| `get_execution_stats()` | Counts: `total_tasks`, `pending`, `blocked`, `running`, `completed`, `failed`, `cancelled` |

Background worker: (1) dependencies -- a task runs once every dependency completed and fails when a dependency failed or was cancelled; an unknown dependency ID keeps it blocked; (2) resources -- `Task.resources` (`TaskResource(resource_type, amount, resource_id=None)`) are allocated from the orchestrator's `ResourceManager` just before execution and released afterwards. A requirement that can never be met (unknown type or ID, type mismatch, amount above capacity, resource offline/maintenance/depleted) fails the task; temporarily insufficient capacity keeps it queued. `retry_count`/`max_retries` and `timeout` are recorded on the task but not enforced by the worker.

### `ResourceManager`

| Field / Method | Description |
| --- | --- |
| `resources: dict[str, Resource]` | Registered resources with capacity and limits |
| `_lock: threading.RLock` | Thread-safe allocation guard |
| `add_resource(resource)` | Register a `Resource` |
| `allocate(resource_id, requester_id, amount)` | Allocate; returns `ResourceAllocation`, or None if unknown, unavailable or short of capacity |
| `release(allocation_id)` | Release allocation, restore capacity |
| `allocate_resources(requester_id, requirements)` / `deallocate_resources(requester_id)` | All-or-nothing multi-resource allocation and bulk release |
| `get_usage(resource_id)` | Return `ResourceUsage` for one resource |
| `get_resource_usage()` | System-wide summary: `total_resources`, `total_allocations` (active), `lifetime_allocations`, `resources_by_type`, `utilization_summary`, per-resource `resources` |

### `WorkflowDAG`

| Field / Method | Description |
| --- | --- |
| `tasks: dict[str, DAGTask]` | Tasks keyed by name |
| `validate_dag()` | Check missing deps, self-deps and DFS cycle detection; returns `(is_valid, errors)` |
| `get_execution_order()` | Kahn's algorithm; returns parallelisable levels of task names |
| `visualize()` | Mermaid flowchart string |

Raises `CycleDetectedError` (subclass of `DAGValidationError`).

### `ParallelExecutor`

Context manager wrapping `ThreadPoolExecutor`. `ParallelExecutor(max_workers=4, timeout=300.0, actions=None)`. `execute_tasks(tasks, dependencies)` dispatches each task's `module`/`action` (see Task Dispatch), runs a task only after its dependencies (the mapping plus the task's own `dependencies` key) completed, fails dependents of a failed task without running them, raises `ValueError` for duplicate names, unknown dependencies or cycles, and returns `dict[str, ExecutionResult]`.

### `ProjectManager`

| Field / Method | Description |
| --- | --- |
| `create_project(name, type, description="", path=None)` | Scaffold `src/`, `tests/`, `config/`, `docs/` dirs under `path` (default `projects_root / name`); generate RASP docs; None if the name is registered or the directory exists |
| `get_project(name)` | Lookup by name |
| `list_projects()` | Return all active `Project` instances |
| `update_project_status(name, status)` | Transition lifecycle status |
| `update_project_metrics(name, metrics)` | Merge into `Project.metrics` |
| `add_project_milestone(name, milestone_name, milestone_data=None)` | Record a timestamped milestone in `Project.milestones` |
| `get_projects_summary()` | `total_projects`, `by_status`, `by_type`, `recent_activity` |

7 project types: `AI_ANALYSIS`, `WEB_APPLICATION`, `DATA_PIPELINE`, `ML_MODEL`, `DOCUMENTATION`, `RESEARCH`, `CUSTOM`.

## Dependencies

- `codomyrmex.logging_monitoring.core.logger_config` -- structured logging
- `codomyrmex.exceptions` -- `TaskExecutionError` for dispatch and resource failures
- `codomyrmex.performance` -- optional `monitor_performance` decorator
- `codomyrmex.model_context_protocol` -- `MCPToolResult`, `MCPErrorDetail` (required for MCP tools)
- `jsonschema` -- not used directly here (used by config_management)
- Standard library: `threading`, `concurrent.futures`, `collections`, `importlib`, `uuid`, `json`, `pathlib`

## Error Handling

- `DAGValidationError` / `CycleDetectedError` -- DAG structural errors
- `ValueError` -- workflow not found, invalid workflow dependencies, unknown task
- `NotImplementedError` -- `WorkflowStep.run_if` conditions
- `TaskExecutionError` -- unresolvable `module`/`action`, unsatisfiable resource requirement (recorded as the task's error)
- `RuntimeError` -- MCP unavailable (zero-mock enforcement)

## Navigation

- **Specification**: This file
- **Agent coordination**: [AGENTS.md](AGENTS.md)
- **Parent**: [orchestration/](../SPEC.md)

## Related Documents

- **Readme**: [README.md](README.md)
