# Task Orchestration Guide

Complete end-to-end guide for task orchestration, from task creation to execution monitoring and result review.

## Overview

Task orchestration in Codomyrmex allows you to coordinate individual tasks with dependency management, resource requirements, and priority-based execution. This guide walks through the complete workflow from creating tasks to reviewing results.

The API lives in `codomyrmex.logistics.orchestration.project` (formerly `codomyrmex.project_orchestration`).

> **How tasks run**: the orchestrator calls `codomyrmex.<module>.<action>(**parameters)`, for example `module="coding.static_analysis", action="analyze_code_quality"`. A function registered with `orchestrator.register_action(module, action, func)` takes precedence, which is how you run code that is not in a `codomyrmex` module. An unknown module or action, or an exception raised by the action, marks the task `FAILED` with the reason in `TaskResult.error`. Resource requirements (`Task.resources`) are allocated from the orchestrator's `ResourceManager` just before the task runs and released when it finishes.

## Quick Start

```python
from codomyrmex.logistics.orchestration.project import (
    get_task_orchestrator,
    Task,
    TaskPriority,
    TaskResource,
    ResourceType
)

# Get the global task orchestrator (4 worker threads)
orchestrator = get_task_orchestrator()

# Start execution engine (submit_task also starts it on demand)
orchestrator.start_processing()

# Create and execute tasks
# ... (see examples below)
```

## Step 1: Create Tasks

### Basic Task Creation

```python
from codomyrmex.logistics.orchestration.project import Task, TaskPriority

# Create a simple task: runs codomyrmex.coding.static_analysis.analyze_code_quality(path="./src")
task = Task(
    name="analyze_code",
    module="coding.static_analysis",
    action="analyze_code_quality",
    parameters={"path": "./src"}
)

# Add task to orchestrator (returns task.id)
task_id = orchestrator.submit_task(task)

# Or register your own function as an action and block until the task finishes
orchestrator.register_action("demo", "echo", lambda message="": message)
result = orchestrator.execute_task(Task(name="greet", module="demo", action="echo", parameters={"message": "hi"}))
print(result.result)  # "hi"
```

### Task with Dependencies

Dependencies are task IDs. A task whose dependencies have not completed is held in the `BLOCKED` state and queued once they finish. If a dependency fails or is cancelled, the dependent task fails without running.

```python
# Create first task
setup_task = Task(
    name="setup_environment",
    module="environment_setup",
    action="validate_environment",
    priority=TaskPriority.HIGH
)

# Create dependent task
analysis_task = Task(
    name="analyze_code",
    module="coding.static_analysis",
    action="analyze_code_quality",
    parameters={"path": "./src"},
    dependencies=[setup_task.id],  # Depends on setup_task
    priority=TaskPriority.NORMAL
)

orchestrator.submit_task(setup_task)
orchestrator.submit_task(analysis_task)
```

### Task with Resources

```python
from codomyrmex.logistics.orchestration.project import TaskResource, ResourceType

task = Task(
    name="heavy_analysis",
    module="coding.static_analysis",
    action="analyze_code_quality",
    parameters={"path": "./src"},
    priority=TaskPriority.HIGH,
    resources=[
        TaskResource(resource_type=ResourceType.COMPUTE.value, amount=2.0, resource_id="sys-compute"),
        TaskResource(resource_type=ResourceType.MEMORY.value, amount=512.0, resource_id="sys-memory"),
    ],
    timeout=600  # recorded on the task; not enforced
)
orchestrator.submit_task(task)
```

## Step 2: Configure Resources and Priorities

### Priority Levels

Ready tasks are dequeued in priority order: `CRITICAL`, `HIGH`, `NORMAL`, `LOW`, `BACKGROUND`.

```python
from codomyrmex.logistics.orchestration.project import TaskPriority

# These use the "demo"/"echo" action registered in Step 1
# Critical priority (executes first)
critical_task = Task(name="hotfix", module="demo", action="echo", priority=TaskPriority.CRITICAL)

# High priority
high_task = Task(name="build", module="demo", action="echo", priority=TaskPriority.HIGH)

# Normal priority (default)
normal_task = Task(name="analyze", module="demo", action="echo", priority=TaskPriority.NORMAL)

# Low priority
low_task = Task(name="report", module="demo", action="echo", priority=TaskPriority.LOW)
```

### Resource Requirements

`TaskResource` takes a resource type string, an amount, and an optional specific resource ID. The default `ResourceManager` registers `sys-compute`, `sys-memory`, and `api-global`.

All of a task's requirements are allocated, all or nothing, immediately before it runs and released when it finishes, fails or is cancelled. Without `resource_id`, the resource of that type with the most free capacity is used. If capacity is only temporarily short, the task stays queued until other tasks release it; a requirement that can never be met (unknown type or resource ID, type mismatch, amount above capacity, resource offline, in maintenance or depleted) fails the task.

```python
# Compute resource
cpu_resource = TaskResource(resource_type=ResourceType.COMPUTE.value, amount=1.0, resource_id="sys-compute")

# Memory resource (MB)
memory_resource = TaskResource(resource_type=ResourceType.MEMORY.value, amount=256.0, resource_id="sys-memory")

# External API quota
api_resource = TaskResource(resource_type=ResourceType.API_QUOTA.value, amount=10.0, resource_id="api-global")

task = Task(
    name="quality_review",
    module="coding.static_analysis",
    action="analyze_code_quality",
    parameters={"path": "./src"},
    resources=[cpu_resource, memory_resource, api_resource]
)
```

### Task Configuration

```python
task = Task(
    name="long_running_task",
    module="coding.static_analysis",
    action="analyze_code_quality",
    parameters={"path": "./src"},
    timeout=3600,  # recorded on the task; not enforced
    max_retries=3,  # Retry budget recorded on the task
    metadata={"description": "Process large dataset", "tags": ["data-processing", "visualization"]}
)
```

## Step 3: Execute Task Workflow

### Start Execution

```python
# Start the execution engine (submit_task calls this automatically)
orchestrator.start_processing()

# Tasks are now processed automatically in the background
```

### Wait for Completion

```python
# Wait for all tasks to reach COMPLETED, FAILED or CANCELLED
completed = orchestrator.wait_for_completion(timeout=300.0)  # 5 minute timeout

if completed:
    print("All tasks finished")
else:
    print("Task execution timed out")
```

### Monitor Execution

```python
import time

# Monitor task status
while True:
    stats = orchestrator.get_execution_stats()
    print(f"Total: {stats['total_tasks']}, Running: {stats['running']}, Completed: {stats['completed']}, Failed: {stats['failed']}")

    if stats['completed'] + stats['failed'] == stats['total_tasks']:
        break

    time.sleep(1)
```

## Step 4: Monitor Execution and Handle Failures

### Check Task Status

```python
# Get task by ID
task = orchestrator.get_task(task_id)

if task:
    print(f"Task status: {task.status.value}")
    print(f"Retry count: {task.retry_count}")
    if task.result:
        print(f"Success: {task.result.success}")
```

### Get Task Result

```python
# Get task result (a TaskResult)
result = orchestrator.get_task_result(task_id)

if result:
    if result.success:
        print(f"Task completed: {result.result}")
        print(f"Execution time: {result.duration}s")
    else:
        print(f"Task failed: {result.error}")
        print(f"Status: {result.status.value}")
```

### Handle Task Failures

```python
from codomyrmex.logistics.orchestration.project import TaskStatus

# Check for failed tasks
failed_tasks = [t for t in orchestrator.list_tasks() if t.status == TaskStatus.FAILED]

for task in failed_tasks:
    result = orchestrator.get_task_result(task.id)
    if result:
        print(f"Task {task.name} failed: {result.error}")

    # Resubmit while retries remain
    if task.retry_count < task.max_retries:
        task.retry_count += 1
        orchestrator.submit_task(task)
```

### Cancel Tasks

```python
# Cancel a task
success = orchestrator.cancel_task(task_id)

if success:
    print("Task cancelled")
else:
    print("Task could not be cancelled (already completed or not found)")
```

## Step 5: Review Results and Performance

### Execution Statistics

```python
# Get execution statistics
stats = orchestrator.get_execution_stats()

print(f"Total tasks: {stats['total_tasks']}")
print(f"Running: {stats['running']}")
print(f"Completed: {stats['completed']}")
print(f"Failed: {stats['failed']}")
```

### Task Results

```python
# Get results for all completed tasks
completed_tasks = [t for t in orchestrator.list_tasks() if t.status == TaskStatus.COMPLETED]

for task in completed_tasks:
    result = orchestrator.get_task_result(task.id)
    if result and result.success:
        print(f"\nTask: {task.name}")
        print(f"  Execution time: {result.duration:.2f}s")
        print(f"  Data: {result.result}")
        print(f"  Metadata: {result.metadata}")
```

### Performance Analysis

```python
# Analyze performance by task
tasks = orchestrator.list_tasks()
execution_times = []

for task in tasks:
    if task.execution_time:
        execution_times.append({
            'name': task.name,
            'time': task.execution_time,
            'priority': task.priority.name
        })

# Sort by execution time
execution_times.sort(key=lambda x: x['time'], reverse=True)

print("Slowest tasks:")
for item in execution_times[:5]:
    print(f"  {item['name']}: {item['time']:.2f}s (priority: {item['priority']})")
```

## Complete Example

```python
from codomyrmex.logistics.orchestration.project import (
    TaskOrchestrator,
    Task,
    TaskPriority,
    TaskResource,
    ResourceType,
)

# Initialize orchestrator
orchestrator = TaskOrchestrator(max_workers=4)
orchestrator.start_processing()

# Create task chain
setup_task = Task(
    name="setup",
    module="environment_setup",
    action="validate_environment",
    priority=TaskPriority.HIGH
)

analysis_task = Task(
    name="analyze",
    module="coding.static_analysis",
    action="analyze_code_quality",
    parameters={"path": "./src"},
    dependencies=[setup_task.id],
    priority=TaskPriority.NORMAL,
    resources=[
        TaskResource(resource_type=ResourceType.COMPUTE.value, amount=1.0)
    ],
    timeout=300
)

visualization_task = Task(
    name="visualize",
    module="data_visualization",
    action="create_bar_chart",
    parameters={"categories": ["errors", "warnings"], "values": [0, 0], "title": "Code Quality"},
    dependencies=[analysis_task.id],
    priority=TaskPriority.NORMAL
)

for task in (setup_task, analysis_task, visualization_task):
    orchestrator.submit_task(task)

# Wait for completion
completed = orchestrator.wait_for_completion(timeout=600)

if completed:
    # Get results
    analysis_result = orchestrator.get_task_result(analysis_task.id)
    visualization_result = orchestrator.get_task_result(visualization_task.id)

    # Print statistics
    stats = orchestrator.get_execution_stats()
    total_time = sum(t.execution_time or 0 for t in orchestrator.list_tasks())
    print(f"Completed {stats['completed']} tasks in {total_time:.2f}s")
else:
    print("Execution timed out")

# Stop execution
orchestrator.stop_execution()
```

## Best Practices

1. **Dependency Management**: Keep dependency chains as short as possible
2. **Resource Requirements**: Declare resource requirements on tasks; they are allocated before the task runs and released afterwards
3. **Priority Setting**: Use appropriate priorities for task importance
4. **Timeout Configuration**: Set realistic timeouts based on expected execution time
5. **Error Handling**: Check task results and handle failures appropriately
6. **Shutdown**: Call `stop_execution()` when you own the orchestrator instance
7. **Monitoring**: Monitor execution statistics for performance optimization

## Troubleshooting

### Tasks Not Executing

- Ensure `start_processing()` has been called (or that tasks were added with `submit_task`)
- Check that dependencies are satisfied (blocked tasks have `TaskStatus.BLOCKED`)
- A task whose resource requirement is temporarily short of capacity stays queued; check `orchestrator.resource_manager.get_resource_usage()`
- Check task status with `orchestrator.get_task(task_id)`

### Tasks Failing

- Check `orchestrator.get_task_result(task_id).error` for details
- Verify that `codomyrmex.<module>` exists and has a public callable named `action`, or register one with `register_action`
- Check parameter names and types: parameters are passed as keyword arguments
- A task whose dependency failed or was cancelled fails without running

### Slow Execution

- Check execution statistics for bottlenecks
- Consider adjusting priorities or `max_workers`
- Verify dependencies are optimal

## Related Documentation

- [Dispatch and Coordination](./dispatch-coordination.md)
- [Resource Configuration](./resource-configuration.md)
- [API Specification](../../src/codomyrmex/logistics/orchestration/project/API_SPECIFICATION.md)

## Navigation Links

- **Parent**: [Project Overview](../README.md)
- **Module Index**: [All Agents](../../AGENTS.md)
- **Documentation**: [Reference Guides](../../docs/README.md)
- **Home**: [Repository Root](../../README.md)
