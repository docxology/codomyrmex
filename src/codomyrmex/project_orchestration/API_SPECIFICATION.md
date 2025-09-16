# Project Orchestration - API Specification

## Introduction

This API specification documents the programmatic interfaces for the Project Orchestration module of Codomyrmex. The module provides comprehensive project management, workflow orchestration, and task coordination capabilities through a set of Python classes and functions.

## Core Classes and Interfaces

### OrchestrationEngine

The main coordination engine that manages all orchestration operations.

#### Methods

##### `create_session(user_id: str = "system", **kwargs) -> str`

- **Description**: Creates a new orchestration session for context management.
- **Parameters**:
  - `user_id` (string): User identifier for the session
  - `mode` (string, optional): Execution mode ("sequential", "parallel", "resource_aware")
  - `max_parallel_tasks` (int, optional): Maximum concurrent tasks (default: 4)
  - `max_parallel_workflows` (int, optional): Maximum concurrent workflows (default: 2)
  - `timeout_seconds` (int, optional): Session timeout in seconds
  - `resource_requirements` (dict, optional): Required resources for the session
  - `metadata` (dict, optional): Additional session metadata
- **Returns**: Session ID (string)
- **Example**:
  ```python
  engine = OrchestrationEngine()
  session_id = engine.create_session(
      user_id="analyst",
      mode="resource_aware",
      max_parallel_tasks=8,
      resource_requirements={"cpu": {"cores": 4}, "memory": {"gb": 8}}
  )
  ```

##### `execute_workflow(workflow_name: str, session_id: str = None, **params) -> Dict[str, Any]`

- **Description**: Executes a workflow with orchestration management.
- **Parameters**:
  - `workflow_name` (string): Name of the workflow to execute
  - `session_id` (string, optional): Session ID for context (creates new if not provided)
  - `**params`: Workflow-specific parameters
- **Returns**: Dictionary with execution results
  ```python
  {
    "success": bool,
    "session_id": str,
    "executed_steps": int,
    "failed_steps": list,
    "results": dict,
    "execution_time": float,
    "error": str  # If success is False
  }
  ```
- **Example**:
  ```python
  result = engine.execute_workflow(
      "ai-analysis",
      code_path="./src",
      output_path="./analysis",
      include_visualization=True
  )
  ```

##### `get_system_status() -> Dict[str, Any]`

- **Description**: Retrieves comprehensive system status and metrics.
- **Returns**: Dictionary with system status information
  ```python
  {
    "timestamp": str,
    "orchestration_engine": {
      "active_sessions": int,
      "event_handlers": dict
    },
    "workflow_manager": {
      "total_workflows": int,
      "running_workflows": int
    },
    "task_orchestrator": {
      "total_tasks": int,
      "pending": int,
      "running": int,
      "completed": int,
      "failed": int
    },
    "project_manager": dict,
    "resource_manager": dict,
    "performance": dict  # If available
  }
  ```

##### `health_check() -> Dict[str, Any]`

- **Description**: Performs comprehensive health check of all components.
- **Returns**: Dictionary with health status
  ```python
  {
    "overall_status": str,  # "healthy", "degraded", "unhealthy"
    "timestamp": str,
    "components": {
      "workflow_manager": {"status": str, "details": dict},
      "task_orchestrator": {"status": str, "details": dict},
      "project_manager": {"status": str, "details": dict},
      "resource_manager": {"status": str, "details": dict}
    },
    "issues": list
  }
  ```

---

### WorkflowManager

Manages workflow definitions and execution.

#### Methods

##### `create_workflow(name: str, description: str = "") -> Workflow`

- **Description**: Creates a new workflow instance.
- **Parameters**:
  - `name` (string): Unique workflow name
  - `description` (string, optional): Workflow description
- **Returns**: Workflow object
- **Example**:
  ```python
  manager = WorkflowManager()
  workflow = manager.create_workflow(
      "custom-analysis",
      "Custom code analysis workflow"
  )
  ```

##### `execute_workflow(name: str, **params) -> Dict[str, Any]`

- **Description**: Executes a workflow synchronously.
- **Parameters**:
  - `name` (string): Workflow name to execute
  - `**params`: Workflow parameters
- **Returns**: Execution result dictionary
- **Example**:
  ```python
  result = manager.execute_workflow(
      "ai-analysis",
      code_path="./src",
      ai_provider="openai"
  )
  ```

##### `list_workflows() -> List[str]`

- **Description**: Lists all available workflow names.
- **Returns**: List of workflow names

##### `get_workflow_status(name: str) -> Optional[Dict[str, Any]]`

- **Description**: Gets detailed status of a specific workflow.
- **Parameters**:
  - `name` (string): Workflow name
- **Returns**: Status dictionary or None if not found
  ```python
  {
    "name": str,
    "status": str,
    "progress": {
      "total_steps": int,
      "completed_steps": int,
      "failed_steps": int,
      "running_steps": int
    },
    "start_time": str,
    "end_time": str,
    "error_message": str
  }
  ```

---

### TaskOrchestrator

Coordinates individual task execution with dependency management.

#### Methods

##### `create_task(name: str, module: str, action: str, **kwargs) -> Task`

- **Description**: Creates and adds a new task.
- **Parameters**:
  - `name` (string): Task name
  - `module` (string): Codomyrmex module name
  - `action` (string): Module action/function
  - `parameters` (dict, optional): Action parameters
  - `dependencies` (list, optional): Task dependencies
  - `priority` (TaskPriority, optional): Task priority
  - `timeout` (int, optional): Timeout in seconds
  - `max_retries` (int, optional): Maximum retry attempts
  - `resources` (list, optional): Required resources
- **Returns**: Task object
- **Example**:
  ```python
  orchestrator = TaskOrchestrator()
  task = orchestrator.create_task(
      "analyze_code",
      "static_analysis",
      "analyze_code_quality",
      parameters={"path": "./src"},
      priority=TaskPriority.HIGH,
      timeout=300
  )
  ```

##### `execute_task(task: Task) -> TaskResult`

- **Description**: Executes a single task synchronously.
- **Parameters**:
  - `task` (Task): Task object to execute
- **Returns**: TaskResult object
  ```python
  {
    "success": bool,
    "data": Any,
    "error_message": str,
    "error_type": str,
    "execution_time": float,
    "memory_usage": float,
    "metadata": dict
  }
  ```

##### `get_execution_stats() -> Dict[str, Any]`

- **Description**: Gets execution statistics.
- **Returns**: Statistics dictionary
  ```python
  {
    "total_tasks": int,
    "pending": int,
    "ready": int,
    "running": int,
    "completed": int,
    "failed": int,
    "cancelled": int,
    "total_execution_time": float,
    "average_execution_time": float
  }
  ```

---

### ProjectManager

High-level project lifecycle management.

#### Methods

##### `create_project(name: str, template_name: str = None, path: str = None, **kwargs) -> Project`

- **Description**: Creates a new project from a template.
- **Parameters**:
  - `name` (string): Project name
  - `template_name` (string, optional): Template to use
  - `path` (string, optional): Project directory path
  - `description` (string, optional): Project description
  - `author` (string, optional): Project author
  - `tags` (list, optional): Project tags
- **Returns**: Project object
- **Example**:
  ```python
  manager = ProjectManager()
  project = manager.create_project(
      "web-app-analysis",
      template_name="web_application",
      description="Analysis of web application code",
      author="Development Team"
  )
  ```

##### `execute_project_workflow(project_name: str, workflow_name: str, **params) -> Dict[str, Any]`

- **Description**: Executes a workflow for a specific project.
- **Parameters**:
  - `project_name` (string): Project name
  - `workflow_name` (string): Workflow to execute
  - `**params`: Workflow parameters
- **Returns**: Execution result dictionary

##### `get_project_status(name: str) -> Optional[Dict[str, Any]]`

- **Description**: Gets detailed project status.
- **Parameters**:
  - `name` (string): Project name
- **Returns**: Status dictionary
  ```python
  {
    "name": str,
    "status": str,  # "planning", "active", "completed", etc.
    "type": str,
    "version": str,
    "path": str,
    "workflows": int,
    "active_workflows": int,
    "required_modules": list,
    "created_at": str,
    "updated_at": str,
    "milestones": dict,
    "metrics": dict
  }
  ```

##### `list_templates() -> List[str]`

- **Description**: Lists available project templates.
- **Returns**: List of template names

---

### ResourceManager

System resource allocation and management.

#### Methods

##### `allocate_resources(user_id: str, requirements: Dict[str, Dict[str, Any]], timeout: int = None) -> Optional[Dict[str, str]]`

- **Description**: Allocates resources to a user based on requirements.
- **Parameters**:
  - `user_id` (string): User/task identifier
  - `requirements` (dict): Resource requirements mapping
  - `timeout` (int, optional): Allocation timeout
- **Returns**: Dictionary mapping requirement keys to allocated resource IDs, or None if failed
- **Example**:
  ```python
  manager = ResourceManager()
  allocation = manager.allocate_resources(
      "task_123",
      {
          "cpu": {"cores": 2},
          "memory": {"gb": 4},
          "disk": {"gb": 10}
      },
      timeout=60
  )
  ```

##### `deallocate_resources(user_id: str, allocation_ids: List[str] = None) -> bool`

- **Description**: Deallocates resources for a user.
- **Parameters**:
  - `user_id` (string): User identifier
  - `allocation_ids` (list, optional): Specific allocations to release
- **Returns**: True if successful

##### `get_resource_usage(resource_id: str = None) -> Dict[str, Any]`

- **Description**: Gets resource usage statistics.
- **Parameters**:
  - `resource_id` (string, optional): Specific resource ID, or None for system-wide
- **Returns**: Usage statistics dictionary

---

## Data Models

### Workflow Class

```python
@dataclass
class Workflow:
    name: str
    description: str = ""
    version: str = "1.0"
    steps: List[WorkflowStep] = field(default_factory=list)
    status: WorkflowStatus = WorkflowStatus.DRAFT
    metadata: Dict[str, Any] = field(default_factory=dict)
    # ... additional fields
```

### WorkflowStep Class

```python
@dataclass
class WorkflowStep:
    name: str
    module: str
    action: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list)
    conditions: Dict[str, Any] = field(default_factory=dict)
    timeout: Optional[int] = None
    # ... additional fields
```

### Task Class

```python
@dataclass
class Task:
    id: str
    name: str
    module: str
    action: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list)
    priority: TaskPriority = TaskPriority.NORMAL
    status: TaskStatus = TaskStatus.PENDING
    # ... additional fields
```

### Project Class

```python
@dataclass
class Project:
    name: str
    description: str = ""
    type: ProjectType = ProjectType.CUSTOM
    path: str = ""
    status: ProjectStatus = ProjectStatus.PLANNING
    workflows: List[str] = field(default_factory=list)
    config: Dict[str, Any] = field(default_factory=dict)
    # ... additional fields
```

### Resource Class

```python
@dataclass
class Resource:
    id: str
    name: str
    type: ResourceType
    status: ResourceStatus = ResourceStatus.AVAILABLE
    capacity: Dict[str, Any] = field(default_factory=dict)
    allocated: Dict[str, Any] = field(default_factory=dict)
    # ... additional fields
```

## Enumerations

### WorkflowStatus
- `DRAFT`: Workflow is being designed
- `READY`: Workflow is ready for execution
- `RUNNING`: Workflow is currently executing
- `PAUSED`: Workflow execution is paused
- `COMPLETED`: Workflow completed successfully
- `FAILED`: Workflow execution failed
- `CANCELLED`: Workflow was cancelled

### TaskStatus
- `PENDING`: Task is waiting to be executed
- `READY`: Task is ready (dependencies satisfied)
- `RUNNING`: Task is currently executing
- `COMPLETED`: Task completed successfully
- `FAILED`: Task execution failed
- `CANCELLED`: Task was cancelled
- `SKIPPED`: Task was skipped

### TaskPriority
- `LOW`: Low priority task
- `NORMAL`: Normal priority task
- `HIGH`: High priority task
- `CRITICAL`: Critical priority task

### ProjectStatus
- `PLANNING`: Project is in planning phase
- `ACTIVE`: Project is actively being worked on
- `PAUSED`: Project work is paused
- `COMPLETED`: Project is completed
- `ARCHIVED`: Project is archived
- `FAILED`: Project failed

### ResourceType
- `CPU`: CPU cores
- `MEMORY`: System memory
- `DISK`: Disk storage
- `NETWORK`: Network bandwidth
- `FILE`: File access
- `DATABASE`: Database connection
- `EXTERNAL_API`: External API quota
- `GPU`: GPU resources

## Error Handling

### Exception Classes

#### `OrchestrationError`
Base exception for orchestration operations.

#### `WorkflowExecutionError`
Raised when workflow execution fails.

#### `TaskExecutionError`
Raised when task execution fails.

#### `ResourceAllocationError`
Raised when resource allocation fails.

#### `ProjectManagementError`
Raised when project operations fail.

### Error Response Format

```python
{
    "success": False,
    "error": str,           # Error message
    "error_type": str,      # Error type/category
    "error_code": str,      # Specific error code
    "details": dict,        # Additional error details
    "suggestions": list     # Suggested remediation steps
}
```

## Configuration

### Environment Variables
- `CODOMYRMEX_ORCHESTRATION_DIR`: Base directory for orchestration data
- `CODOMYRMEX_MAX_WORKERS`: Maximum number of worker threads
- `CODOMYRMEX_RESOURCE_CONFIG`: Path to resource configuration file

### Configuration File Format (JSON)
```json
{
  "max_workers": 4,
  "workflows_dir": "./workflows",
  "projects_dir": "./projects", 
  "templates_dir": "./templates",
  "resource_config": "./resources.json",
  "performance_monitoring": true,
  "session_timeout": 3600,
  "cleanup_interval": 300
}
```

## Integration Examples

### Basic Workflow Execution
```python
from codomyrmex.project_orchestration import OrchestrationEngine

engine = OrchestrationEngine()
result = engine.execute_workflow(
    "ai-analysis",
    code_path="./src",
    output_path="./reports",
    ai_provider="openai"
)

if result['success']:
    print(f"Analysis completed in {result['execution_time']} seconds")
    print(f"Results: {result['results']}")
else:
    print(f"Analysis failed: {result['error']}")
```

### Project-based Development
```python
from codomyrmex.project_orchestration import ProjectManager

pm = ProjectManager()

# Create project
project = pm.create_project(
    "chatbot-analysis",
    template_name="ai_analysis",
    description="AI analysis of chatbot conversations"
)

# Execute project workflow
result = pm.execute_project_workflow(
    "chatbot-analysis",
    "ai-analysis",
    data_path="./conversations",
    focus_areas=["sentiment", "intent", "quality"]
)

# Track milestone
pm.add_project_milestone(
    "chatbot-analysis",
    "initial_analysis_complete",
    {"quality_score": 8.5, "insights_generated": 23}
)
```

### Custom Task Orchestration
```python
from codomyrmex.project_orchestration import TaskOrchestrator, TaskPriority

orchestrator = TaskOrchestrator()
orchestrator.start_execution()

# Create dependent tasks
analysis_task = orchestrator.create_task(
    "analyze_code",
    "static_analysis",
    "analyze_code_quality",
    parameters={"path": "./src"},
    priority=TaskPriority.HIGH
)

visualization_task = orchestrator.create_task(
    "create_chart", 
    "data_visualization",
    "create_bar_chart",
    parameters={
        "data": "${analyze_code.result}",
        "title": "Code Quality Metrics"
    },
    dependencies=[analysis_task.id],
    priority=TaskPriority.NORMAL
)

# Wait for completion
orchestrator.wait_for_completion(timeout=300)

# Get results
stats = orchestrator.get_execution_stats()
print(f"Completed {stats['completed']} tasks")
```

## Performance Considerations

- **Resource Management**: Always specify resource requirements for better allocation
- **Parallel Execution**: Use parallel mode for independent tasks and workflows
- **Caching**: Results are cached based on parameters and dependencies
- **Monitoring**: Enable performance monitoring for production deployments
- **Cleanup**: Sessions and resources are automatically cleaned up

## Rate Limiting

- **Workflow Execution**: Limited by available workers and resources
- **Task Execution**: Limited by task orchestrator configuration
- **Resource Allocation**: Subject to system resource limits
- **API Calls**: External API calls respect provider rate limits

## Versioning

This API follows semantic versioning. Breaking changes to method signatures or return values will result in a major version update, while backward-compatible enhancements will result in minor version updates.

Current API Version: **1.0.0**
