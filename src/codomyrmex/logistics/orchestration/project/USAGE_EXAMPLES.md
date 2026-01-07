# Codomyrmex Orchestration Usage Examples

This document provides comprehensive usage examples for the Codomyrmex Project Orchestration module.

## 🔄 Basic Workflow Management

### Creating a Simple Workflow

```python
from codomyrmex.logistics.orchestration.project import get_workflow_manager, WorkflowStep

# Get workflow manager
wf_manager = get_workflow_manager()

# Define workflow steps
steps = [
    WorkflowStep(
        name="environment_check",
        module="environment_setup",
        action="check_environment",
        parameters={}
    ),
    WorkflowStep(
        name="code_analysis",
        module="static_analysis",
        action="analyze_code_quality",
        parameters={"path": "."},
        dependencies=["environment_check"]
    )
]

# Create workflow
success = wf_manager.create_workflow("code_analysis_workflow", steps)
print(f"Workflow created: {success}")
```

### Executing a Workflow

```python
# Execute workflow
result = wf_manager.execute_workflow("code_analysis_workflow")
print(f"Workflow status: {result.status}")
```

## 🏗️ Project Lifecycle Management

### Creating a Project from Template

```python
from codomyrmex.logistics.orchestration.project import get_project_manager

# Get project manager
project_manager = get_project_manager()

# Create project from template
project = project_manager.create_project(
    name="my_ai_project",
    template_name="ai_analysis",
    description="AI-powered code analysis project"
)

print(f"Created project: {project.name}")
print(f"Project type: {project.type.value}")
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
    action="check_environment",
    priority=TaskPriority.HIGH
)

analysis_task = Task(
    name="analyze_code",
    module="static_analysis",
    action="analyze_code_quality",
    parameters={"path": "."},
    dependencies=[setup_task.id],
    priority=TaskPriority.NORMAL
)

# Add tasks and execute
task_orchestrator.add_task(setup_task)
task_orchestrator.add_task(analysis_task)
task_orchestrator.start_execution()
```

## 🤖 AI Integration with MCP Tools

### Using MCP Tools for Workflow Execution

```python
from codomyrmex.logistics.orchestration.project import get_mcp_tools

# Get MCP tools
tools = get_mcp_tools()

# Execute workflow via AI
result = tools.execute_tool("execute_workflow", {
    "workflow_name": "code_analysis_workflow",
    "parameters": {"path": "."}
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
        action="check_environment",
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

# Execute workflow (handles errors gracefully)
result = wf_manager.execute_workflow("error_test_workflow")
print(f"Workflow status: {result.status}")
print(f"Errors: {result.errors}")
```

## 🚀 Advanced Scenarios

### Multi-Project Workflow

```python
from codomyrmex.logistics.orchestration.project import get_orchestration_engine

# Get orchestration engine
engine = get_orchestration_engine()

# Create multiple projects
projects = ["project1", "project2", "project3"]
for project_name in projects:
    project = project_manager.create_project(
        name=project_name,
        template_name="ai_analysis"
    )
    print(f"Created project: {project.name}")

# Execute workflow for each project
for project_name in projects:
    result = engine.execute_project_workflow(
        project_name,
        "ai-analysis",
        path=f"./projects/{project_name}"
    )
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
logger = logging.getLogger('codomyrmex.project_orchestration')
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
- **Documentation**: [Reference Guides](../../../docs/README.md)
- **Home**: [Root README](../../../README.md)
