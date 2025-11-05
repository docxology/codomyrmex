# Codomyrmex Project Orchestration Module

The Project Orchestration module provides comprehensive project management and task orchestration capabilities that integrate all other Codomyrmex modules into cohesive workflows. This module serves as the central coordination hub for complex multi-module operations.

## 🎯 Key Features

- **Workflow Management**: Define, execute, and monitor complex workflows
- **Task Orchestration**: Coordinate individual tasks with dependency management
- **Project Lifecycle Management**: Create, manage, and track projects from templates
- **Resource Management**: Allocate and monitor system resources
- **Performance Monitoring**: Track execution performance across all components
- **AI Integration**: MCP tools for AI-driven orchestration
- **Error Handling**: Robust error handling and recovery mechanisms

## 🏗️ Architecture

The orchestration module consists of five main components:

### 1. WorkflowManager
Manages workflow definitions and execution with performance monitoring.

**Key Features:**
- Create and manage workflow definitions
- Execute workflows asynchronously
- Track workflow performance metrics
- Handle workflow dependencies

**Example:**
```python
from codomyrmex.project_orchestration import get_workflow_manager, WorkflowStep

# Get workflow manager
wf_manager = get_workflow_manager()

# Create workflow steps
steps = [
    WorkflowStep(
        name="analyze_code",
        module="static_analysis",
        action="analyze_code_quality",
        parameters={"path": "."}
    ),
    WorkflowStep(
        name="generate_insights",
        module="ai_code_editing",
        action="generate_code_insights",
        parameters={"analysis_data": "{{analyze_code.output}}"},
        dependencies=["analyze_code"]
    )
]

# Create workflow
wf_manager.create_workflow("ai_analysis", steps)

# Execute workflow
result = wf_manager.execute_workflow("ai_analysis")
```

### 2. TaskOrchestrator
Coordinates individual task execution with dependency management and resource control.

**Key Features:**
- Priority-based task scheduling
- Dependency resolution
- Resource allocation and locking
- Retry logic and error handling
- Parallel execution support

**Example:**
```python
from codomyrmex.project_orchestration import get_task_orchestrator, Task, TaskPriority

# Get task orchestrator
task_orchestrator = get_task_orchestrator()

# Create tasks
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
    dependencies=[task1.id],
    priority=TaskPriority.NORMAL
)

# Add tasks and execute
task_orchestrator.add_task(task1)
task_orchestrator.add_task(task2)
task_orchestrator.start_execution()
```

### 3. ProjectManager
High-level project lifecycle management with templates and scaffolding.

**Key Features:**
- Project creation from templates
- Project status tracking
- Milestone management
- Configuration management
- Project archiving

**Example:**
```python
from codomyrmex.project_orchestration import get_project_manager

# Get project manager
project_manager = get_project_manager()

# Create project from template
project = project_manager.create_project(
    name="my_ai_project",
    template_name="ai_analysis",
    description="AI-powered code analysis project"
)

# Get project status
status = project_manager.get_project_status("my_ai_project")
```

### 4. ResourceManager
Manages system resources and their allocation.

**Key Features:**
- Resource allocation and deallocation
- Resource usage monitoring
- Resource contention handling
- Automatic cleanup of expired allocations

**Example:**
```python
from codomyrmex.project_orchestration import get_resource_manager

# Get resource manager
resource_manager = get_resource_manager()

# Allocate resources
requirements = {
    "cpu": {"cores": 2},
    "memory": {"gb": 4}
}
allocated = resource_manager.allocate_resources("user123", requirements)

# Use resources...
# Deallocate when done
resource_manager.deallocate_resources("user123")
```

### 5. OrchestrationEngine
Main coordinator that integrates all components.

**Key Features:**
- Session management
- Complex workflow execution
- Event handling
- System health monitoring
- Performance metrics collection

**Example:**
```python
from codomyrmex.project_orchestration import get_orchestration_engine

# Get orchestration engine
engine = get_orchestration_engine()

# Create session
session_id = engine.create_session(
    user_id="user123",
    mode="resource_aware",
    max_parallel_tasks=4
)

# Execute workflow
result = engine.execute_workflow("ai_analysis", session_id)

# Get system status
status = engine.get_system_status()
```

## 🚀 Quick Start

### 1. Basic Workflow Execution

```python
from codomyrmex.project_orchestration import get_orchestration_engine

# Get orchestration engine
engine = get_orchestration_engine()

# Execute a simple workflow
result = engine.execute_workflow("ai_analysis")
print(f"Workflow completed: {result['success']}")
```

### 2. Project Creation

```python
from codomyrmex.project_orchestration import get_project_manager

# Get project manager
project_manager = get_project_manager()

# Create project
project = project_manager.create_project(
    name="my_project",
    template_name="web_application"
)

print(f"Created project: {project.name}")
```

### 3. Task Orchestration

```python
from codomyrmex.project_orchestration import get_task_orchestrator, Task

# Get task orchestrator
task_orchestrator = get_task_orchestrator()

# Create and execute task
task = Task(
    name="analyze_code",
    module="static_analysis",
    action="analyze_code_quality",
    parameters={"path": "."}
)

result = task_orchestrator.execute_task(task)
print(f"Task completed: {result.success}")
```

## 🛠️ CLI Usage

The orchestration module integrates with the Codomyrmex CLI:

```bash
# List available workflows
codomyrmex workflow list

# Create a new workflow
codomyrmex workflow create my-workflow --template ai-analysis

# Execute a workflow
codomyrmex workflow run ai-analysis

# List projects
codomyrmex project list

# Create a project
codomyrmex project create my-project --template web_application

# Check orchestration status
codomyrmex orchestration status

# Check system health
codomyrmex orchestration health
```

## 🤖 AI Integration (MCP Tools)

The module provides MCP (Model Context Protocol) tools for AI-driven orchestration:

```python
from codomyrmex.project_orchestration import get_mcp_tools

# Get MCP tools
tools = get_mcp_tools()

# Execute workflow via AI
result = tools.execute_tool("execute_workflow", {
    "workflow_name": "ai_analysis",
    "parameters": {"path": "."}
})

# Create project via AI
result = tools.execute_tool("create_project", {
    "name": "ai_project",
    "template": "ai_analysis",
    "description": "AI-powered analysis project"
})
```

### Available MCP Tools

- `execute_workflow`: Execute a workflow
- `create_workflow`: Create a new workflow
- `list_workflows`: List available workflows
- `create_project`: Create a new project
- `list_projects`: List available projects
- `execute_task`: Execute a single task
- `get_system_status`: Get system status
- `get_health_status`: Get health status
- `allocate_resources`: Allocate system resources
- `create_complex_workflow`: Create and execute complex workflows

## 📊 Performance Monitoring

The orchestration module integrates with Codomyrmex's performance monitoring system:

```python
from codomyrmex.project_orchestration import get_workflow_manager

# Get workflow manager with performance monitoring
wf_manager = get_workflow_manager()

# Execute workflow (automatically monitored)
result = wf_manager.execute_workflow("ai_analysis")

# Get performance summary
perf_summary = wf_manager.get_performance_summary()
print(f"Performance metrics: {perf_summary}")
```

## 🔧 Configuration

### Resource Configuration

Resources can be configured via the ResourceManager:

```python
from codomyrmex.project_orchestration import get_resource_manager, Resource, ResourceType

# Get resource manager
resource_manager = get_resource_manager()

# Add custom resource
custom_resource = Resource(
    id="gpu_1",
    name="GPU Resource",
    type=ResourceType.GPU,
    capacity={"units": 1},
    limits=ResourceLimits(max_concurrent_users=1)
)

resource_manager.add_resource(custom_resource)
```

### Workflow Configuration

Workflows can be configured with various parameters:

```python
# Create workflow with custom configuration
steps = [
    WorkflowStep(
        name="analyze",
        module="static_analysis",
        action="analyze_code_quality",
        parameters={"path": "."},
        timeout=300,  # 5 minutes timeout
        max_retries=3
    )
]

wf_manager.create_workflow("custom_workflow", steps)
```

## 🧪 Testing

The module includes comprehensive integration tests:

```bash
# Run integration tests
python testing/integration/integration_test.py

# Run orchestration examples
python scripts/project_orchestration/examples.py
```

## 📈 Monitoring and Health Checks

### System Health Check

```python
from codomyrmex.project_orchestration import get_orchestration_engine

# Get orchestration engine
engine = get_orchestration_engine()

# Perform health check
health = engine.health_check()
print(f"System health: {health['overall_status']}")

# Check component health
for component, status in health['components'].items():
    print(f"{component}: {status['status']}")
```

### Performance Metrics

```python
# Get comprehensive metrics
metrics = engine.get_metrics()
print(f"Active sessions: {metrics['sessions']['total']}")
print(f"Total workflows: {metrics['workflows']}")
print(f"Resource utilization: {metrics['resources']}")
```

## 🔒 Error Handling

The orchestration module provides robust error handling:

- **Workflow-level errors**: Workflows continue execution even if individual steps fail
- **Task-level errors**: Tasks can be retried with exponential backoff
- **Resource errors**: Automatic cleanup of failed resource allocations
- **Dependency errors**: Clear error messages for circular dependencies

## 🚀 Advanced Usage

### Custom Event Handlers

```python
from codomyrmex.project_orchestration import get_orchestration_engine

# Get orchestration engine
engine = get_orchestration_engine()

# Register event handler
def on_workflow_completed(event, data):
    print(f"Workflow {data['workflow_name']} completed: {data['success']}")

engine.register_event_handler('workflow_completed', on_workflow_completed)
```

### Complex Workflow Definitions

```python
# Define complex workflow with parallel execution
workflow_definition = {
    "steps": [
        {"name": "setup", "module": "environment_setup", "action": "check_environment"},
        {"name": "analyze", "module": "static_analysis", "action": "analyze_code_quality"},
        {"name": "visualize", "module": "data_visualization", "action": "create_chart"}
    ],
    "dependencies": {
        "analyze": ["setup"],
        "visualize": ["analyze"]
    },
    "parallel_groups": [
        ["analyze", "visualize"]  # These can run in parallel
    ]
}

result = engine.execute_complex_workflow(workflow_definition)
```

## 📚 API Reference

For detailed API documentation, see:
- [WorkflowManager API](workflow_manager.py)
- [TaskOrchestrator API](task_orchestrator.py)
- [ProjectManager API](project_manager.py)
- [ResourceManager API](resource_manager.py)
- [OrchestrationEngine API](orchestration_engine.py)
- [MCP Tools API](mcp_tools.py)

## 🤝 Contributing

To contribute to the orchestration module:

1. Follow the existing code style and patterns
2. Add comprehensive tests for new features
3. Update documentation for API changes
4. Ensure all components work together properly

## 📄 License

This module is part of the Codomyrmex project and follows the same license terms.