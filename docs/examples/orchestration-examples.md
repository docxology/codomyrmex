# Orchestration Examples Guide

> **Status: partially stale.** The former `codomyrmex.project_orchestration` package now lives at `codomyrmex.logistics.orchestration.project` (`get_orchestration_engine`, `get_workflow_manager`, `get_task_orchestrator`, `get_resource_manager`, `WorkflowStep`, `Task`, …); the Python snippets in the later sections use that API. Examples 1-4 refer to `scripts/project_orchestration/examples.py`, which no longer exists; see `scripts/logistics/examples/` and the [Task Orchestration Guide](../project_orchestration/task-orchestration-guide.md) instead. Script-runner orchestration lives separately in `codomyrmex.orchestrator`.

Documentation for orchestration examples demonstrating task, project, and workflow orchestration with complete configuration files.

## Overview

Orchestration examples demonstrate the complete orchestration system including:

- Task orchestration with dependencies
- Project lifecycle management
- Workflow execution and coordination
- Resource management
- Session management

## Main Orchestration Examples File

**File**: `scripts/project_orchestration/examples.py`

**Purpose**: Comprehensive demonstration of all orchestration capabilities.

**Examples Included**:

1. Basic workflow creation and execution
2. Project creation and management
3. Task orchestration with dependencies
4. Resource management and allocation
5. End-to-end orchestration workflows

## Example 1: Basic Workflow Creation

**Purpose**: Create and execute a basic workflow with multiple steps.

**Configuration File**: See `config/examples/workflow-basic.json` (created below)

**Execution**:

```python
python scripts/project_orchestration/examples.py
# Select option 1 or run specific function
```

**Expected Output**:

- Workflow created successfully
- Workflow executed
- Step results available
- Performance metrics collected

## Example 2: Project Management

**Purpose**: Create and manage projects from templates.

**Configuration**: Uses existing project templates

**Execution**:

```python
from scripts.project_orchestration.examples import example_2_project_management
example_2_project_management()
```

**Expected Output**:

- Project created from template
- Directory structure created
- Documentation generated
- Project status available

## Example 3: Task Orchestration

**Purpose**: Coordinate tasks with dependencies and resources.

**Configuration**: See task configuration below

**Execution**:

```python
from scripts.project_orchestration.examples import example_3_task_orchestration
example_3_task_orchestration()
```

**Expected Output**:

- Tasks created with dependencies
- Resources allocated
- Tasks executed in order
- Execution statistics available

## Example 4: Resource Management

**Purpose**: Demonstrate resource allocation and monitoring.

**Configuration**: Uses `resources.json`

**Execution**:

```python
from scripts.project_orchestration.examples import example_4_resource_management
example_4_resource_management()
```

**Expected Output**:

- Resources listed
- Resources allocated
- Usage statistics available
- Resources deallocated

## Configuration Files

### Basic Workflow Configuration

Create `config/examples/workflow-basic.json`:

```json
{
  "name": "basic_analysis",
  "steps": [
    {
      "name": "check_env",
      "module": "environment_setup",
      "action": "check_environment",
      "parameters": {},
      "dependencies": [],
      "timeout": 60,
      "max_retries": 3
    },
    {
      "name": "analyze",
      "module": "static_analysis",
      "action": "analyze_code_quality",
      "parameters": {"path": "."},
      "dependencies": ["check_env"],
      "timeout": 300,
      "max_retries": 2
    }
  ]
}
```

### Workflow with Dependencies

Create `config/examples/workflow-with-dependencies.json`:

```json
{
  "name": "complex_analysis",
  "steps": [
    {
      "name": "setup",
      "module": "environment_setup",
      "action": "check_environment",
      "parameters": {},
      "dependencies": []
    },
    {
      "name": "analyze_code",
      "module": "static_analysis",
      "action": "analyze_code_quality",
      "parameters": {"path": "."},
      "dependencies": ["setup"]
    },
    {
      "name": "ai_insights",
      "module": "agents",
      "action": "generate_code_insights",
      "parameters": {"analysis_data": "{{analyze_code.output}}"},
      "dependencies": ["analyze_code"]
    },
    {
      "name": "visualize",
      "module": "data_visualization",
      "action": "create_bar_chart",
      "parameters": {"data": "{{ai_insights.output}}"},
      "dependencies": ["ai_insights"]
    }
  ]
}
```

## Complete Orchestration Example

### Creating and Executing a Complete Workflow

```python
from codomyrmex.logistics.orchestration.project import (
    get_task_orchestrator,
    get_workflow_manager,
    WorkflowStep
)

def complete_orchestration_example():
    # 1. Create workflow
    wf_manager = get_workflow_manager()

    steps = [
        WorkflowStep(
            name="setup",
            module="environment_setup",
            action="check_environment"
        ),
        WorkflowStep(
            name="analyze",
            module="static_analysis",
            action="analyze_code_quality",
            parameters={"path": "."},
            dependencies=["setup"]
        ),
        WorkflowStep(
            name="visualize",
            module="data_visualization",
            action="create_bar_chart",
            parameters={"data": "{{analyze.output}}"},
            dependencies=["analyze"]
        )
    ]

    wf_manager.create_workflow("complete_workflow", steps)

    # 2. Execute workflow (steps are submitted to the task orchestrator)
    execution = wf_manager.execute_workflow("complete_workflow")
    orchestrator = get_task_orchestrator()

    # 3. Review results
    if orchestrator.wait_for_completion(timeout=600):
        for task in orchestrator.list_tasks():
            print(f"{task.name}: {task.status.value}")
    else:
        print(f"Workflow {execution.execution_id} did not finish in time")

complete_orchestration_example()
```

## Project Creation Example

### Creating a Project and Executing Workflow

```python
from codomyrmex.logistics.orchestration.project import (
    ProjectType,
    get_project_manager,
    get_workflow_manager,
)

# Create project
pm = get_project_manager()
project = pm.create_project(
    name="analysis_project",
    type=ProjectType.AI_ANALYSIS,
    description="AI analysis project"
)

# Execute a registered workflow for it
if project:
    execution = get_workflow_manager().execute_workflow(
        "complete_workflow", path=str(project.path / "src")
    )
    print(f"Project created; workflow {execution.execution_id} is {execution.status.value}")
```

## Task Orchestration Example

### Complete Task Workflow

```python
from codomyrmex.logistics.orchestration.project import (
    get_task_orchestrator,
    Task,
    TaskPriority,
    TaskResource,
    ResourceType
)

orchestrator = get_task_orchestrator()
orchestrator.start_processing()

# Create task chain
task1 = Task(
    name="setup",
    module="environment_setup",
    action="check_environment",
    priority=TaskPriority.HIGH
)

task2 = Task(
    name="analyze",
    module="static_analysis",
    action="analyze_code_quality",
    parameters={"path": "."},
    dependencies=[task1.id],
    priority=TaskPriority.NORMAL,
    resources=[
        TaskResource(resource_type=ResourceType.COMPUTE.value, amount=1.0, resource_id="sys-compute")
    ]
)

orchestrator.submit_task(task1)
orchestrator.submit_task(task2)

# Wait for completion
completed = orchestrator.wait_for_completion(timeout=600)

if completed:
    result = orchestrator.get_task_result(task2.id)
    if result and result.success:
        print(f"Analysis completed: {result.result}")
```

## Validation and Testing

### Validate Configuration

```python
# Validate workflow configuration
from codomyrmex.logistics.orchestration.project import WorkflowManager, WorkflowStep

manager = WorkflowManager()
steps = [
    WorkflowStep(name="step1", module="module1", action="action1"),
    WorkflowStep(name="step2", module="module2", action="action2", dependencies=["step1"])
]

# Dependencies are validated explicitly; create_workflow stores the steps as given
step_dicts = [{"name": s.name, "dependencies": s.dependencies} for s in steps]
assert manager.validate_workflow_dependencies(step_dicts) == []
assert manager.create_workflow("test_workflow", steps), "Workflow creation failed"
```

### Test Execution

```python
# Test workflow execution
from codomyrmex.logistics.orchestration.project import (
    TaskStatus,
    WorkflowStatus,
    get_task_orchestrator,
)

def test_workflow():
    # Reuses `manager` from the previous snippet
    execution = manager.execute_workflow("test_workflow")
    assert execution.status == WorkflowStatus.RUNNING  # returned before steps finish

    orchestrator = get_task_orchestrator()
    assert orchestrator.wait_for_completion(timeout=60)
    assert all(t.status == TaskStatus.COMPLETED for t in orchestrator.list_tasks())
    print("Workflow test passed")

test_workflow()
```

## Expected Results

### Workflow Execution

- ✅ Workflow created and saved
- ✅ Steps executed in dependency order
- ✅ Results available for each step
- ✅ Performance metrics collected
- ✅ Error handling working

### Project Management

- ✅ Project created from template
- ✅ Directory structure created
- ✅ Documentation generated
- ✅ Project configuration saved
- ✅ Status tracking working

### Task Orchestration

- ✅ Tasks created with dependencies
- ✅ Resources allocated correctly
- ✅ Tasks executed in proper order
- ✅ Results available
- ✅ Statistics accurate

### Resource Management

- ✅ Resources listed
- ✅ Allocation successful
- ✅ Usage tracked
- ✅ Deallocation working
- ✅ Health checks passing

## Troubleshooting

### Workflow Execution Failures

**Issue**: Workflow fails to execute

**Solutions**:

- Check workflow configuration syntax
- Verify module and action names
- Review dependency chains
- Check resource availability

### Project Creation Failures

**Issue**: Project creation fails

**Solutions**:

- Verify template exists
- Check directory permissions
- Review template configuration
- Ensure required modules available

### Task Execution Issues

**Issue**: Tasks not executing

**Solutions**:

- Verify `start_processing()` called
- Check dependencies satisfied
- Review resource allocation
- Check task status

## Related Documentation

- [Task Orchestration Guide](../project_orchestration/task-orchestration-guide.md)
- [Project Lifecycle Guide](../project_orchestration/project-lifecycle-guide.md)
- [Config-Driven Operations](../project_orchestration/config-driven-operations.md)
- [Dispatch and Coordination](../project_orchestration/dispatch-coordination.md)

## Navigation Links

- **Parent**: [Project Overview](../README.md)
- **Module Index**: [All Agents](../../AGENTS.md)
- **Documentation**: [Reference Guides](../../docs/README.md)
- **Home**: [Repository Root](../../README.md)
