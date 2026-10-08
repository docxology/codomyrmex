# Codomyrmex Orchestration Usage Examples

This document provides comprehensive usage examples for the Codomyrmex Project Orchestration module.

## 🔄 Basic Workflow Management

### Creating a Simple Workflow

```python
from codomyrmex.logistics.orchestration.project import get_workflow_manager, WorkflowStep

# Get workflow manager
wf_manager = get_workflow_manager()

# Define workflow steps. Each step calls codomyrmex.<module>.<action>(**parameters);
# list order does not matter, dependencies (step names) decide execution order.
steps = [
    WorkflowStep(
        name="environment_check",
        module="environment_setup",
        action="validate_environment",
        parameters={}
    ),
    WorkflowStep(
        name="code_analysis",
        module="coding.static_analysis",
        action="analyze_project",
        parameters={"project_root": "."},
        dependencies=["environment_check"]
    )
]

# Create workflow (in memory only)
success = wf_manager.create_workflow("code_analysis_workflow", steps)
print(f"Workflow created: {success}")
```

### Saving a Workflow for Later Processes

```python
from codomyrmex.logistics.orchestration.project import WorkflowManager

# persist=True writes config/workflows/production/code_analysis_workflow.json
# (under the current directory); invalid steps raise before anything is written.
wf_manager.create_workflow("code_analysis_workflow", steps, persist=True)
print(wf_manager.workflow_files["code_analysis_workflow"])

# A manager created later (e.g. by `codomyrmex workflow run`) loads the file.
later = WorkflowManager()
assert later.get_workflow("code_analysis_workflow") == steps
```

Step parameters are passed to the action verbatim; `{{step.output}}`
substitution is not supported, so steps cannot consume each other's results.

### Executing a Workflow

```python
# Execute workflow: blocks until every step has finished
result = wf_manager.execute_workflow("code_analysis_workflow")
print(f"Workflow status: {result.status}")  # COMPLETED or FAILED
print(f"Step results: {result.step_results}")
print(f"Errors: {result.error}")
```

Functions that are not part of a `codomyrmex` module can be registered on the
task orchestrator the workflow manager uses:

```python
wf_manager.task_orchestrator.register_action("reports", "summarise", my_function)
```

## 🏗️ Project Lifecycle Management

### Creating a Project from Template

```python
from codomyrmex.logistics.orchestration.project import ProjectType, get_project_manager

# Get project manager
project_manager = get_project_manager()

# Create project of a given type
project = project_manager.create_project(
    name="my_ai_project",
    type=ProjectType.AI_ANALYSIS,
    description="AI-powered code analysis project"
)

print(f"Created project: {project.name}")
print(f"Project type: {project.type.value}")
```

### Project Persistence

```python
from codomyrmex.logistics.orchestration.project import ProjectManager, ProjectStatus

# create_project saved my_ai_project/project.json; updates save it again.
project_manager.update_project_status("my_ai_project", ProjectStatus.PAUSED)
project_manager.update_project_metrics("my_ai_project", {"runs": 1})

# A new manager rooted at the same directory registers the saved projects.
reloaded = ProjectManager(projects_root=project_manager.projects_root)
assert reloaded.get_project("my_ai_project").status is ProjectStatus.PAUSED
```

## ⚙️ Task Orchestration

### Creating Tasks with Dependencies

```python
from codomyrmex.logistics.orchestration.project import get_task_orchestrator, Task, TaskPriority

# Get task orchestrator
task_orchestrator = get_task_orchestrator()

# Create tasks with dependencies
setup_task = Task(
    name="setup_environment",
    module="environment_setup",
    action="validate_environment",
    priority=TaskPriority.HIGH
)

analysis_task = Task(
    name="analyze_code",
    module="coding.static_analysis",
    action="analyze_project",
    parameters={"project_root": "."},
    dependencies=[setup_task.id],
    priority=TaskPriority.NORMAL
)

# Add tasks and execute
task_orchestrator.submit_task(setup_task)
task_orchestrator.submit_task(analysis_task)
task_orchestrator.start_processing()
```

## 🤖 AI Integration with MCP Tools

### Using MCP Tools for Workflow Execution

```python
from codomyrmex.logistics.orchestration.project import get_mcp_tools

# Get MCP tools
tools = get_mcp_tools()

# Execute workflow via AI ("parameters" would be merged into every step's
# parameters, so the steps must all accept them)
result = tools.execute_tool("execute_workflow", {
    "workflow_name": "code_analysis_workflow",
})

print(f"Workflow execution result: {result.success}")
```

### Creating Projects via AI

```python
# Create project via AI
result = tools.execute_tool("create_project", {
    "name": "ai_powered_analysis",
    "template": "ai_analysis",
    "description": "AI-powered code analysis project"
})

if result.success:
    print(f"Project created: {result.data['project_name']}")
```

## 📊 Performance Monitoring

### Basic Performance Monitoring

```python
from codomyrmex.logistics.orchestration.project import get_workflow_manager

# Get workflow manager with performance monitoring
wf_manager = get_workflow_manager()

# Execute workflow (automatically monitored)
result = wf_manager.execute_workflow("code_analysis_workflow")

# Get performance summary
perf_summary = wf_manager.get_performance_summary()
print(f"Performance summary: {perf_summary}")
```

## 🚨 Error Handling and Recovery

### Workflow Error Handling

```python
# Create workflow with error-prone step
error_steps = [
    WorkflowStep(
        name="valid_step",
        module="environment_setup",
        action="validate_environment",
        parameters={}
    ),
    WorkflowStep(
        name="error_step",
        module="nonexistent_module",
        action="nonexistent_action",
        parameters={},
        dependencies=["valid_step"]
    )
]

wf_manager.create_workflow("error_test_workflow", error_steps)

# Execute workflow: the unknown module fails "error_step" and the workflow
result = wf_manager.execute_workflow("error_test_workflow")
print(f"Workflow status: {result.status}")  # WorkflowStatus.FAILED
print(f"Errors: {result.error}")  # "error_step: ... codomyrmex.nonexistent_module ..."
```

## 🚀 Advanced Scenarios

### Multi-Project Workflow

```python
from codomyrmex.logistics.orchestration.project import ProjectType, get_orchestration_engine

# Get orchestration engine
engine = get_orchestration_engine()

# Create multiple projects (the global engine shares the global project manager)
projects = ["project1", "project2", "project3"]
for project_name in projects:
    project = engine.project_manager.create_project(
        name=project_name,
        type=ProjectType.AI_ANALYSIS
    )
    print(f"Created project: {project.name}")

# Execute a registered workflow for each project. Keyword arguments would be
# merged into every step's parameters, so pass only ones all steps accept.
for project_name in projects:
    result = engine.execute_project_workflow(project_name, "code_analysis_workflow")
    print(f"Project {project_name} workflow: {result['success']}")
```

### Event-Driven Orchestration

```python
# Register event handlers
def on_workflow_completed(event, data):
    print(f"Workflow {data['workflow_name']} completed: {data['success']}")

# Register handlers
engine.register_event_handler('workflow_completed', on_workflow_completed)

# Create session and execute workflow
session_id = engine.create_session(user_id="event_user")
result = engine.execute_workflow("code_analysis_workflow", session_id)
```

## 🔍 Debugging and Troubleshooting

### Debug Mode

```python
import logging

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('codomyrmex.logistics.orchestration.project')
logger.setLevel(logging.DEBUG)

# Execute workflow with debug info
result = wf_manager.execute_workflow("code_analysis_workflow")
```

### Health Monitoring

```python
# Get system health
health = engine.health_check()
print(f"System health: {health['overall_status']}")

# Check component health
for component, status in health['components'].items():
    print(f"{component}: {status['status']}")
```

This guide covers the main usage patterns for the Codomyrmex Project Orchestration module. For more details, see the API documentation and integration tests.

## Navigation Links

- **Parent**: [Project Overview](../README.md)
- **Module Index**: [All Agents](../../AGENTS.md)
- **Documentation**: [Reference Guides](../../../../../docs/README.md)
- **Home**: [Root README](../../../README.md)
