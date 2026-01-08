# Orchestration Examples Guide

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
      "module": "ai_code_editing",
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
from codomyrmex.project_orchestration import (
    get_orchestration_engine,
    get_workflow_manager,
    WorkflowStep
)
import asyncio

async def complete_orchestration_example():
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
    
    # 2. Execute workflow
    engine = get_orchestration_engine()
    result = engine.execute_workflow("complete_workflow")
    
    # 3. Review results
    if result['success']:
        print(f"Workflow completed: {result['steps_executed']} steps")
    else:
        print(f"Workflow failed: {result.get('error')}")

asyncio.run(complete_orchestration_example())
```

## Project Creation Example

### Creating a Project and Executing Workflow

```python
from codomyrmex.project_orchestration import get_orchestration_engine

engine = get_orchestration_engine()

# Create project and execute workflow
result = engine.create_project_from_workflow(
    project_name="analysis_project",
    workflow_name="ai-analysis",
    template_name="ai_analysis",
    description="AI analysis project"
)

if result['success']:
    print("Project created and workflow executed")
    print(f"Results: {result['workflow_result']}")
```

## Task Orchestration Example

### Complete Task Workflow

```python
from codomyrmex.project_orchestration import (
    get_task_orchestrator,
    Task,
    TaskPriority,
    TaskResource,
    ResourceType
)

orchestrator = get_task_orchestrator()
orchestrator.start_execution()

# Create task chain
task1 = orchestrator.create_task(
    name="setup",
    module="environment_setup",
    action="check_environment",
    priority=TaskPriority.HIGH
)

task2 = orchestrator.create_task(
    name="analyze",
    module="static_analysis",
    action="analyze_code_quality",
    parameters={"path": "."},
    dependencies=[task1.id],
    priority=TaskPriority.NORMAL,
    resources=[
        TaskResource(type=ResourceType.CPU, identifier="system_cpu", mode="read")
    ]
)

# Wait for completion
completed = orchestrator.wait_for_completion(timeout=600)

if completed:
    result = orchestrator.get_task_result(task2.id)
    if result and result.success:
        print(f"Analysis completed: {result.data}")
```

## Validation and Testing

### Validate Configuration

```python
# Validate workflow configuration
from codomyrmex.project_orchestration import WorkflowManager, WorkflowStep

manager = WorkflowManager()
steps = [
    WorkflowStep(name="step1", module="module1", action="action1"),
    WorkflowStep(name="step2", module="module2", action="action2", dependencies=["step1"])
]

# Validation happens during creation
success = manager.create_workflow("test_workflow", steps)
assert success, "Workflow creation failed"
```

### Test Execution

```python
# Test workflow execution
import asyncio
from codomyrmex.project_orchestration import get_workflow_manager

async def test_workflow():
    manager = get_workflow_manager()
    execution = await manager.execute_workflow("test_workflow")
    assert execution.status == WorkflowStatus.COMPLETED
    print("Workflow test passed")

asyncio.run(test_workflow())
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
- Verify `start_execution()` called
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
- **Home**: [Repository Root](../../../README.md)
