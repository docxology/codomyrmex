# Task Orchestration Guide

Complete end-to-end guide for task orchestration, from task creation to execution monitoring and result review.

## Overview

Task orchestration in Codomyrmex allows you to coordinate individual tasks with dependency management, resource allocation, and priority-based execution. This guide walks through the complete workflow from creating tasks to reviewing results.

## Quick Start

```python
from codomyrmex.project_orchestration import (
    get_task_orchestrator,
    Task,
    TaskPriority,
    TaskResource,
    ResourceType
)

# Get task orchestrator
orchestrator = get_task_orchestrator()

# Start execution engine
orchestrator.start_execution()

# Create and execute tasks
# ... (see examples below)
```

## Step 1: Create Tasks

### Basic Task Creation

```python
from codomyrmex.project_orchestration import Task, TaskPriority

# Create a simple task
task = Task(
    name="analyze_code",
    module="static_analysis",
    action="analyze_code_quality",
    parameters={"path": "./src"}
)

# Add task to orchestrator
task_id = orchestrator.add_task(task)
```

### Task with Dependencies

```python
# Create first task
setup_task = orchestrator.create_task(
    name="setup_environment",
    module="environment_setup",
    action="check_environment",
    parameters={},
    priority=TaskPriority.HIGH
)

# Create dependent task
analysis_task = orchestrator.create_task(
    name="analyze_code",
    module="static_analysis",
    action="analyze_code_quality",
    parameters={"path": "./src"},
    dependencies=[setup_task.id],  # Depends on setup_task
    priority=TaskPriority.NORMAL
)
```

### Task with Resources

```python
from codomyrmex.project_orchestration import TaskResource, ResourceType

task = orchestrator.create_task(
    name="heavy_analysis",
    module="static_analysis",
    action="comprehensive_analysis",
    parameters={"path": "./src"},
    priority=TaskPriority.HIGH,
    resources=[
        TaskResource(
            type=ResourceType.CPU,
            identifier="system_cpu",
            mode="read"
        ),
        TaskResource(
            type=ResourceType.MEMORY,
            identifier="system_memory",
            mode="read"
        )
    ],
    timeout=600  # 10 minute timeout
)
```

## Step 2: Configure Resources and Priorities

### Priority Levels

```python
from codomyrmex.project_orchestration import TaskPriority

# Critical priority (executes first)
critical_task = Task(..., priority=TaskPriority.CRITICAL)

# High priority
high_task = Task(..., priority=TaskPriority.HIGH)

# Normal priority (default)
normal_task = Task(..., priority=TaskPriority.NORMAL)

# Low priority
low_task = Task(..., priority=TaskPriority.LOW)
```

### Resource Requirements

```python
# CPU resource
cpu_resource = TaskResource(
    type=ResourceType.CPU,
    identifier="system_cpu",
    mode="read"  # or "write" or "exclusive"
)

# Memory resource
memory_resource = TaskResource(
    type=ResourceType.MEMORY,
    identifier="system_memory",
    mode="read"
)

# External API resource
api_resource = TaskResource(
    type=ResourceType.EXTERNAL_API,
    identifier="openai_api",
    mode="exclusive"
)

task = Task(
    ...,
    resources=[cpu_resource, memory_resource, api_resource]
)
```

### Task Configuration

```python
task = Task(
    name="long_running_task",
    module="data_visualization",
    action="process_large_dataset",
    parameters={"file": "large_data.csv"},
    timeout=3600,  # 1 hour timeout
    max_retries=3,  # Retry up to 3 times
    retry_delay=5.0,  # Wait 5 seconds between retries
    tags=["data-processing", "visualization"],
    metadata={"description": "Process large dataset"}
)
```

## Step 3: Execute Task Workflow

### Start Execution

```python
# Start the execution engine (must be called before tasks execute)
orchestrator.start_execution()

# Tasks are now processed automatically in the background
```

### Wait for Completion

```python
# Wait for all tasks to complete
completed = orchestrator.wait_for_completion(timeout=300.0)  # 5 minute timeout

if completed:
    print("All tasks completed successfully")
else:
    print("Task execution timed out or failed")
```

### Monitor Execution

```python
import time

# Monitor task status
while True:
    stats = orchestrator.get_execution_stats()
    print(f"Pending: {stats['pending']}, Running: {stats['running']}, Completed: {stats['completed']}")
    
    if stats['pending'] == 0 and stats['running'] == 0:
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
# Get task result
result = orchestrator.get_task_result(task_id)

if result:
    if result.success:
        print(f"Task completed: {result.data}")
        print(f"Execution time: {result.execution_time}s")
    else:
        print(f"Task failed: {result.error_message}")
        print(f"Error type: {result.error_type}")
```

### Handle Task Failures

```python
# Check for failed tasks
failed_tasks = orchestrator.list_tasks(status=TaskStatus.FAILED)

for task in failed_tasks:
    result = orchestrator.get_task_result(task.id)
    if result:
        print(f"Task {task.name} failed: {result.error_message}")
        
        # Check if task can be retried
        if task.can_retry():
            # Reset task and retry
            task.status = TaskStatus.PENDING
            task.retry_count = 0
            orchestrator.add_task(task)
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
# Get comprehensive execution statistics
stats = orchestrator.get_execution_stats()

print(f"Total tasks: {stats['total_tasks']}")
print(f"Completed: {stats['completed']}")
print(f"Failed: {stats['failed']}")
print(f"Average execution time: {stats['average_execution_time']:.2f}s")
print(f"Total execution time: {stats['total_execution_time']:.2f}s")
```

### Task Results

```python
# Get results for all completed tasks
completed_tasks = orchestrator.list_tasks(status=TaskStatus.COMPLETED)

for task in completed_tasks:
    result = orchestrator.get_task_result(task.id)
    if result and result.success:
        print(f"
Task: {task.name}")
        print(f"  Execution time: {result.execution_time:.2f}s")
        print(f"  Data: {result.data}")
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
            'priority': task.priority.value
        })

# Sort by execution time
execution_times.sort(key=lambda x: x['time'], reverse=True)

print("Slowest tasks:")
for item in execution_times[:5]:
    print(f"  {item['name']}: {item['time']:.2f}s (priority: {item['priority']})")
```

## Complete Example

```python
from codomyrmex.project_orchestration import (
    get_task_orchestrator,
    Task,
    TaskPriority,
    TaskResource,
    ResourceType,
    TaskStatus
)

# Initialize orchestrator
orchestrator = get_task_orchestrator(max_workers=4)
orchestrator.start_execution()

# Create task chain
setup_task = orchestrator.create_task(
    name="setup",
    module="environment_setup",
    action="check_environment",
    priority=TaskPriority.HIGH
)

analysis_task = orchestrator.create_task(
    name="analyze",
    module="static_analysis",
    action="analyze_code_quality",
    parameters={"path": "./src"},
    dependencies=[setup_task.id],
    priority=TaskPriority.NORMAL,
    resources=[
        TaskResource(type=ResourceType.CPU, identifier="system_cpu", mode="read")
    ],
    timeout=300
)

visualization_task = orchestrator.create_task(
    name="visualize",
    module="data_visualization",
    action="create_bar_chart",
    parameters={"data": "placeholder", "title": "Code Quality"},
    dependencies=[analysis_task.id],
    priority=TaskPriority.NORMAL
)

# Wait for completion
completed = orchestrator.wait_for_completion(timeout=600)

if completed:
    # Get results
    analysis_result = orchestrator.get_task_result(analysis_task.id)
    visualization_result = orchestrator.get_task_result(visualization_task.id)
    
    # Print statistics
    stats = orchestrator.get_execution_stats()
    print(f"Completed {stats['completed']} tasks in {stats['total_execution_time']:.2f}s")
    
    # Stop execution
    orchestrator.stop_execution()
else:
    print("Execution timed out or failed")
```

## Best Practices

1. **Dependency Management**: Keep dependency chains as short as possible
2. **Resource Allocation**: Specify resource requirements for better scheduling
3. **Priority Setting**: Use appropriate priorities for task importance
4. **Timeout Configuration**: Set realistic timeouts based on expected execution time
5. **Error Handling**: Check task results and handle failures appropriately
6. **Resource Cleanup**: Resources are automatically released, but ensure tasks complete
7. **Monitoring**: Monitor execution statistics for performance optimization

## Troubleshooting

### Tasks Not Executing

- Ensure `start_execution()` has been called
- Check that dependencies are satisfied
- Verify resources are available
- Check task status with `orchestrator.get_task(task_id)`

### Tasks Failing

- Check `task.result.error_message` for details
- Verify module and action exist
- Check parameter types and values
- Review resource availability

### Slow Execution

- Check execution statistics for bottlenecks
- Review resource allocation
- Consider adjusting priorities
- Verify dependencies are optimal

## Related Documentation

- [Dispatch and Coordination](./dispatch-coordination.md)
- [Resource Configuration](./resource-configuration.md)
- [API Specification](../../src/codomyrmex/project_orchestration/API_SPECIFICATION.md)


## Navigation Links

- **Parent**: [Project Overview](../README.md)
- **Module Index**: [All Agents](../../AGENTS.md)
- **Documentation**: [Reference Guides](../../docs/README.md)
- **Home**: [Root README](../../../README.md)
