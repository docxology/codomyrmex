# Dispatch and Coordination Patterns

This document describes how tasks and workflows are dispatched, how coordination works between components, and the patterns used for managing execution across the Codomyrmex orchestration system.

## Overview

The Codomyrmex orchestration system uses a multi-layered dispatch and coordination architecture:

1. **Task Dispatch**: Individual tasks are dispatched through a priority queue with dependency resolution
2. **Workflow Dispatch**: Workflow steps are dispatched in dependency order with parallel execution support
3. **Session Coordination**: OrchestrationEngine coordinates sessions and manages cross-component communication
4. **Event System**: Event-driven coordination allows components to react to system changes

## Task Dispatch

### Priority Queue Algorithm

Tasks are scheduled using a priority queue that orders tasks by:
1. **Priority**: Higher priority tasks execute first (CRITICAL > HIGH > NORMAL > LOW)
2. **Creation Time**: Earlier tasks execute first when priorities are equal
3. **Dependencies**: Tasks with satisfied dependencies are eligible for execution

#### Queue Implementation

```python
class TaskQueue:
    def add_task(self, task: Task):
        # Priority queue uses negative priority for max-heap behavior
        priority_value = -task.priority.value
        self.queue.put((priority_value, task.created_at.timestamp(), task.id))
    
    def get_next_ready_task(self, completed_tasks: set[str]) -> Optional[Task]:
        # Returns the highest priority task whose dependencies are satisfied
        ...
```

#### Priority Levels

- **CRITICAL** (4): System-critical tasks that must execute immediately
- **HIGH** (3): Important tasks that should execute soon
- **NORMAL** (2): Standard tasks (default)
- **LOW** (1): Low-priority tasks that can wait

### Dependency Resolution

Tasks declare dependencies on other tasks by ID:

```python
task1 = Task(name="setup", module="environment_setup", action="check")
task2 = Task(
    name="analyze",
    module="static_analysis",
    action="analyze_code",
    dependencies=[task1.id]  # task2 depends on task1
)
```

#### Dependency Checking

A task is ready to execute when:
1. All dependency task IDs are in the `completed_tasks` set
2. Task status is `PENDING`
3. Required resources are available

```python
def is_ready(self, completed_tasks: set[str]) -> bool:
    return (
        self.status == TaskStatus.PENDING and
        all(dep_id in completed_tasks for dep_id in self.dependencies)
    )
```

#### Dependency Graph Example

```
Task A (no dependencies)
  ├─> Task B (depends on A)
  │    └─> Task D (depends on B)
  └─> Task C (depends on A)
       └─> Task E (depends on C)
```

Execution order: A → (B, C) → (D, E)

### Resource Acquisition

Before executing a task, the system attempts to acquire all required resources:

```python
# 1. Check resource availability
if not resource_manager.acquire_resources(task):
    # Resources not available, try again later
    continue

# 2. Execute task
execute_task(task)

# 3. Release resources when done
resource_manager.release_resources(task)
```

#### Resource Acquisition Process

1. **Lock Resources**: Acquire locks for all required resources
2. **Check Availability**: Verify resources are available for the requested mode
3. **Allocate**: Mark resources as allocated to the task
4. **Execute**: Run the task with acquired resources
5. **Release**: Free resources when task completes or fails

#### Resource Modes

- **read**: Multiple tasks can read simultaneously
- **write**: Exclusive access required (no other users)
- **exclusive**: Only one task can use the resource

### Execution Scheduling

Tasks are executed asynchronously in worker threads:

```python
def _execution_loop(self):
    while not self.shutdown_requested:
        # Get next ready task
        task = self.task_queue.get_next_ready_task(self.completed_tasks)
        
        if task is None:
            time.sleep(0.1)  # No ready tasks, wait
            continue
        
        # Try to acquire resources
        if not self.resource_manager.acquire_resources(task):
            time.sleep(0.1)  # Resources not available, retry
            continue
        
        # Execute task asynchronously
        self._execute_task_async(task)
```

## Workflow Dispatch

### Step Execution Order

Workflow steps are executed in dependency order, not definition order:

```python
async def execute_workflow(self, name: str, ...):
    steps = self.workflows[name]
    completed_steps = set()
    remaining_steps = list(steps)
    
    while remaining_steps:
        # Find steps that can be executed (dependencies satisfied)
        ready_steps = [
            step for step in remaining_steps
            if all(dep in completed_steps for dep in step.dependencies)
        ]
        
        # Execute ready steps
        for step in ready_steps:
            result = await self._execute_step(step, parameters, execution)
            completed_steps.add(step.name)
            remaining_steps.remove(step)
```

### Parallel Execution

Independent workflow steps can execute in parallel when:
1. Steps have no dependencies on each other
2. Resources are available for all steps
3. OrchestrationEngine is configured with `mode="parallel"` or `mode="resource_aware"`

#### Example Parallel Execution

```
Step A (no dependencies)
  ├─> Step B (depends on A)
  └─> Step C (depends on A)

Step B and Step C can execute in parallel after Step A completes.
```

### Error Handling and Propagation

#### Step-Level Errors

- Failed steps are retried up to `max_retries` times
- After retries exhausted, step is marked as failed
- Error is recorded in `execution.errors`

#### Workflow-Level Errors

- Workflow continues executing independent steps even if some fail
- Workflow status is `FAILED` if any step fails
- All errors are collected in `execution.errors`
- Partial results available in `execution.results`

### Retry Logic

Workflow steps support retry logic:

```python
@dataclass
class WorkflowStep:
    max_retries: int = 3  # Maximum retry attempts
    
    # Retry happens automatically during execution
    # Current retry_count is tracked internally
```

Retry behavior:
- Retries happen automatically on failure
- No exponential backoff currently (future enhancement)
- Each retry uses the same parameters
- After max retries, step is marked as failed

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

```
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

```
1. OrchestrationEngine.execute_workflow()
   └─> 2. WorkflowManager.execute_workflow()
        └─> 3. For each step:
             ├─> 4. ResourceManager.allocate_resources()
             ├─> 5. Execute step (module.action)
             └─> 6. ResourceManager.deallocate_resources()
   
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
- [API Specification](../../src/codomyrmex/project_orchestration/API_SPECIFICATION.md)

