# Dispatch and Coordination Patterns

This document describes how tasks and workflows are dispatched, how coordination works between components, and the patterns used for managing execution across the Codomyrmex orchestration system.

## Overview

The Codomyrmex orchestration system uses a multi-layered dispatch and coordination architecture:

1. **Task Dispatch**: Individual tasks are dispatched through a priority queue with dependency resolution
2. **Workflow Dispatch**: Workflow steps are dispatched in dependency order with parallel execution support
3. **Session Coordination**: OrchestrationEngine coordinates sessions and manages cross-component communication
4. **Event System**: Event-driven coordination allows components to react to system changes

## Task Dispatch

### Action Resolution

A task names the code it runs with `module` and `action`, and the orchestrator calls it with the task's parameters as keyword arguments:

1. A callable registered with `TaskOrchestrator.register_action(module, action, func)` is used first.
2. Otherwise `codomyrmex.<module>` is imported (`module` may be dotted, e.g. `coding.static_analysis`) and its public attribute `<action>` is called.
3. If the callable returns an awaitable, it is run to completion in the worker thread.

```python
from codomyrmex.logistics.orchestration.project import Task, get_task_orchestrator

orchestrator = get_task_orchestrator()
result = orchestrator.execute_task(
    Task(
        name="analyze",
        module="coding.static_analysis",
        action="analyze_code_quality",
        parameters={"path": "./src"},
    )
)
print(result.status, result.error)
```

An unknown or malformed module or action, or an exception raised by the callable, marks the task `FAILED` with the reason in `TaskResult.error`. A task is only `COMPLETED` when its callable ran and returned.

### Priority Queues

Ready tasks wait in one FIFO queue per priority; the worker always takes the oldest task of the most urgent non-empty priority:

- **CRITICAL** (0)
- **HIGH** (1)
- **NORMAL** (2, default)
- **LOW** (3)
- **BACKGROUND** (4)

At most `max_workers` tasks run concurrently.

### Dependency Resolution

Tasks declare dependencies on other tasks by ID:

```python
task1 = Task(name="setup", module="environment_setup", action="validate_environment")
task2 = Task(
    name="analyze",
    module="coding.static_analysis",
    action="analyze_code_quality",
    dependencies=[task1.id],  # task2 depends on task1
)
```

#### Dependency Checking

When a task is submitted, and whenever the worker is idle:

1. If every dependency is `COMPLETED`, the task becomes `READY` and is queued.
2. If any dependency is `FAILED` or `CANCELLED`, the task is failed without running (its error names the dependency).
3. Otherwise (a dependency is still pending or its ID is unknown) the task stays `BLOCKED`.

#### Dependency Graph Example

```text
Task A (no dependencies)
  ├─> Task B (depends on A)
  │    └─> Task D (depends on B)
  └─> Task C (depends on A)
       └─> Task E (depends on C)
```

Execution order: A → (B, C) → (D, E)

### Resource Acquisition

`Task.resources` lists `TaskResource(resource_type, amount=1.0, resource_id=None)` requirements. Immediately before a queued task runs, the orchestrator allocates all of them from its `ResourceManager` (all or nothing) and releases them when the task finishes, fails or is cancelled:

```python
from codomyrmex.logistics.orchestration.project import Task, TaskResource

task = Task(
    name="heavy_analysis",
    module="coding.static_analysis",
    action="analyze_code_quality",
    resources=[TaskResource(resource_type="memory", amount=512)],
)
```

- With `resource_id`, that resource is used and its type must match `resource_type`; otherwise the resource of that `ResourceType` with the most free capacity is chosen.
- If capacity is only temporarily short, the task goes back to its queue and is retried once running tasks release capacity.
- If the requirement can never be met (unknown type or ID, type mismatch, non-positive amount, amount above capacity, resource offline, in maintenance or depleted), the task fails explicitly.

### Execution Scheduling

```text
# Simplified view of TaskOrchestrator._process_queue (pseudo-code)
while not stopped:
    task_id = next_ready_task()          # highest priority, capacity permitting
    if task_id is None:
        promote_or_fail_blocked_tasks()  # dependency checking (above)
        sleep(0.1)
    elif not start(task_id):             # allocates resources, then runs the action
        sleep(0.05)                      # resources busy: task re-queued
```

## Workflow Dispatch

### Step Execution Order

`WorkflowManager.execute_workflow(name, **params)` is synchronous. It validates the step graph, submits the steps to the task orchestrator in topological order of their `dependencies` (step names), waits for all of them, and returns the finished `WorkflowExecution`. Listing order does not matter: a step listed before its dependency still waits for it.

- Missing dependencies, cycles and duplicate step names raise `ValueError` before any step runs.
- Steps with a `run_if` condition raise `NotImplementedError`; conditions are not supported.
- `params` are merged over every step's `parameters`.

### Parallel Execution

Independent workflow steps execute in parallel (up to the orchestrator's `max_workers`) once their dependencies have completed:

```text
Step A (no dependencies)
  ├─> Step B (depends on A)
  └─> Step C (depends on A)

Step B and Step C can execute in parallel after Step A completes.
```

### Error Handling and Propagation

#### Step-Level Errors

- A step fails when its action cannot be resolved or raises; the error is recorded in `execution.step_results[step]["error"]`.
- A step whose dependency failed is failed without running.
- Steps are not retried: `retry_count`/`max_retries` are recorded but not acted on.

#### Workflow-Level Errors

- Independent steps keep running even if some steps fail.
- The workflow is `FAILED` if any `required` step did not complete; `execution.error` lists each such step and its error.
- `execution.step_results` holds every step's result; `execution.end_time` is always set.
- `WorkflowManager.execute_steps(..., timeout=...)` cancels unfinished steps and fails the workflow when the timeout expires.

## Session Coordination

### Session Lifecycle

OrchestrationEngine manages sessions for coordinating complex operations:

```python
# 1. Create session
session_id = engine.create_session(
    user_id="analyst",
    mode="resource_aware",
    max_parallel_tasks=4
)

# 2. Execute workflows/tasks in session context
result = engine.execute_workflow("ai-analysis", session_id=session_id)

# 3. Close session (cleanup resources)
engine.close_session(session_id)
```

### Session States

- **PENDING**: Session created but not started
- **ACTIVE**: Session is active and executing operations
- **COMPLETED**: Session completed successfully
- **CANCELLED**: Session was cancelled
- **FAILED**: Session failed

### Context Management

Sessions provide:

- **Resource Allocation**: Resources allocated to session are tracked
- **Execution Context**: All operations in session share context
- **Cleanup**: Resources automatically deallocated when session closes
- **Timeout**: Sessions can have timeouts for automatic cleanup

## Event System

### Event Types

The OrchestrationEngine supports event-driven coordination:

- **session_created**: Fired when a session is created
- **session_closed**: Fired when a session is closed
- **workflow_completed**: Fired when a workflow completes
- **task_completed**: Fired when a task completes (future enhancement)

### Event Handlers

Register event handlers to react to system events:

```python
def on_workflow_completed(event: str, data: dict):
    print(f"Workflow {data['workflow_name']} completed: {data['success']}")

engine.register_event_handler('workflow_completed', on_workflow_completed)
```

### Event-Driven Coordination

Components can coordinate through events:

```python
# Component A completes operation
engine.emit_event('operation_complete', {'result': result})

# Component B reacts to event
def handle_operation_complete(event, data):
    # Trigger next operation
    engine.execute_workflow('next_workflow', **data['result'])

engine.register_event_handler('operation_complete', handle_operation_complete)
```

## Cross-Component Communication

### Component Interaction

The OrchestrationEngine coordinates multiple components:

```text
OrchestrationEngine
├── WorkflowManager (workflow definitions and execution)
├── TaskOrchestrator (task scheduling and execution)
├── ProjectManager (project lifecycle)
└── ResourceManager (resource allocation)
```

### Communication Patterns

1. **Direct Calls**: Components call each other directly
2. **Event-Driven**: Components communicate via events
3. **Shared State**: Components share state through OrchestrationEngine
4. **Resource Coordination**: ResourceManager coordinates resource access

### Example: Workflow Execution Flow

```text
1. OrchestrationEngine.execute_workflow()
   ├─> 2. ResourceManager.allocate_resources()   (session resource_requirements)
   └─> 3. WorkflowManager.execute_workflow()
        └─> 4. For each step, in topological order:
             └─> TaskOrchestrator.submit_task()
                  ├─> allocate Task.resources
                  ├─> call codomyrmex.<module>.<action>(**parameters)
                  └─> release Task.resources
        └─> 5. Wait for every step; set status, error, end_time
   └─> 6. ResourceManager.deallocate_resources()  (session)
7. OrchestrationEngine.emit_event('workflow_completed')
```

## Execution Modes

### Sequential Mode

Execute workflows/tasks one after another:

```python
session_id = engine.create_session(mode="sequential")
```

### Parallel Mode

Execute workflows/tasks in parallel when possible:

```python
session_id = engine.create_session(
    mode="parallel",
    max_parallel_tasks=8,
    max_parallel_workflows=4
)
```

### Priority Mode

Execute based on priority ordering:

```python
session_id = engine.create_session(mode="priority")
```

### Resource-Aware Mode

Execute based on resource availability (default):

```python
session_id = engine.create_session(mode="resource_aware")
```

## Coordination Best Practices

1. **Resource Management**: Always specify resource requirements for better allocation
2. **Dependencies**: Keep dependency chains as short as possible
3. **Error Handling**: Configure appropriate retry counts and timeouts
4. **Session Management**: Create sessions for related operations and close when done
5. **Event Handlers**: Use events for loose coupling between components
6. **Parallel Execution**: Design workflows to maximize parallelism

## Related Documentation

- [Task Orchestration Guide](./task-orchestration-guide.md)
- [Workflow Configuration Schema](./workflow-configuration-schema.md)
- [Resource Configuration](./resource-configuration.md)
- [API Specification](../../src/codomyrmex/logistics/orchestration/project/API_SPECIFICATION.md)

## Navigation Links

- **Parent**: [Project Overview](../README.md)
- **Module Index**: [All Agents](../../AGENTS.md)
- **Documentation**: [Reference Guides](../../docs/README.md)
- **Home**: [Repository Root](../../README.md)
