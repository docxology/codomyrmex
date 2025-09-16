# Comprehensive API Documentation - Project Orchestration

This document provides complete API documentation for the Codomyrmex Project Orchestration system, including all classes, methods, and their usage examples.

## Table of Contents

1. [WorkflowManager](#workflowmanager)
2. [TaskOrchestrator](#taskorchestrator)
3. [ProjectManager](#projectmanager)
4. [ResourceManager](#resourcemanager)
5. [OrchestrationEngine](#orchestrationengine)
6. [Data Classes](#data-classes)
7. [Integration Examples](#integration-examples)

---

## WorkflowManager

The `WorkflowManager` class manages workflow definitions, execution, and persistence.

### Class Definition

```python
class WorkflowManager:
    def __init__(self, config_dir: Optional[Path] = None, enable_performance_monitoring: bool = True)
```

### Methods

#### `create_workflow(name: str, steps: List[WorkflowStep], save: bool = True) -> bool`

Creates a new workflow with the specified steps.

**Parameters:**
- `name` (str): Unique name for the workflow
- `steps` (List[WorkflowStep]): List of workflow steps to execute
- `save` (bool): Whether to persist the workflow to disk

**Returns:**
- `bool`: True if workflow was created successfully

**Example:**
```python
from codomyrmex.project_orchestration import get_workflow_manager, WorkflowStep

manager = get_workflow_manager()

steps = [
    WorkflowStep(
        name="analyze",
        module="static_analysis",
        action="analyze_code_quality",
        parameters={"path": "."}
    ),
    WorkflowStep(
        name="visualize",
        module="data_visualization",
        action="create_chart",
        dependencies=["analyze"]
    )
]

success = manager.create_workflow("code_analysis", steps)
```

#### `list_workflows() -> Dict[str, Dict[str, Any]]`

Lists all available workflows with metadata.

**Returns:**
- `Dict[str, Dict[str, Any]]`: Dictionary mapping workflow names to their metadata

**Example:**
```python
workflows = manager.list_workflows()
for name, info in workflows.items():
    print(f"Workflow: {name}")
    print(f"  Steps: {info['steps']}")
    print(f"  Modules: {', '.join(info['modules'])}")
    print(f"  Estimated Duration: {info['estimated_duration']}s")
```

#### `execute_workflow(name: str, parameters: Optional[Dict[str, Any]] = None, timeout: Optional[int] = None) -> WorkflowExecution`

Executes a workflow asynchronously with performance monitoring.

**Parameters:**
- `name` (str): Name of the workflow to execute
- `parameters` (Optional[Dict[str, Any]]): Global parameters for workflow steps
- `timeout` (Optional[int]): Maximum execution time in seconds

**Returns:**
- `WorkflowExecution`: Execution result containing status, results, errors, and metrics

**Example:**
```python
execution = await manager.execute_workflow(
    "code_analysis",
    parameters={"project_path": "/path/to/project"}
)

if execution.status == WorkflowStatus.COMPLETED:
    print("Workflow completed successfully")
    for step_name, result in execution.results.items():
        print(f"Step {step_name}: {result}")
else:
    print(f"Workflow failed: {execution.errors}")
```

#### `get_performance_summary(workflow_name: Optional[str] = None) -> Dict[str, Any]`

Gets comprehensive performance summary for workflows.

**Parameters:**
- `workflow_name` (Optional[str]): Specific workflow name to analyze

**Returns:**
- `Dict[str, Any]`: Performance summary with execution statistics

**Example:**
```python
summary = manager.get_performance_summary()
print(f"Total executions: {summary['total_workflows_executed']}")
print(f"Success rate: {summary['successful_executions'] / summary['total_workflows_executed'] * 100:.1f}%")
```

---

## TaskOrchestrator

The `TaskOrchestrator` class manages individual task execution with dependency management and resource control.

### Class Definition

```python
class TaskOrchestrator:
    def __init__(self, max_workers: int = 4)
```

### Methods

#### `add_task(task: Task) -> str`

Adds a task to the orchestrator.

**Parameters:**
- `task` (Task): Task to add

**Returns:**
- `str`: Task ID

**Example:**
```python
from codomyrmex.project_orchestration import get_task_orchestrator, Task, TaskPriority

orchestrator = get_task_orchestrator()

task = Task(
    name="analyze_code",
    module="static_analysis",
    action="analyze_code_quality",
    priority=TaskPriority.HIGH,
    parameters={"path": "."}
)

task_id = orchestrator.add_task(task)
```

#### `create_task(name: str, module: str, action: str, **kwargs) -> Task`

Creates and adds a new task.

**Parameters:**
- `name` (str): Task name
- `module` (str): Module name
- `action` (str): Action name
- `**kwargs`: Additional task parameters

**Returns:**
- `Task`: Created task instance

**Example:**
```python
task = orchestrator.create_task(
    name="test_task",
    module="module",
    action="action",
    priority=TaskPriority.NORMAL,
    timeout=300,
    dependencies=["setup_task"]
)
```

#### `get_task(task_id: str) -> Optional[Task]`

Gets a task by ID.

**Parameters:**
- `task_id` (str): Task ID

**Returns:**
- `Optional[Task]`: Task instance or None if not found

#### `list_tasks(status: Optional[TaskStatus] = None) -> List[Task]`

Lists tasks, optionally filtered by status.

**Parameters:**
- `status` (Optional[TaskStatus]): Filter by task status

**Returns:**
- `List[Task]`: List of tasks

**Example:**
```python
# List all tasks
all_tasks = orchestrator.list_tasks()

# List only pending tasks
pending_tasks = orchestrator.list_tasks(TaskStatus.PENDING)
```

#### `start_execution()`

Starts the task execution engine.

**Example:**
```python
orchestrator.start_execution()
```

#### `stop_execution()`

Stops the task execution engine.

**Example:**
```python
orchestrator.stop_execution()
```

---

## ProjectManager

The `ProjectManager` class manages high-level project lifecycle with templates and scaffolding.

### Class Definition

```python
class ProjectManager:
    def __init__(self, projects_dir: Optional[str] = None, templates_dir: Optional[str] = None)
```

### Methods

#### `create_project(name: str, description: str = "", template_name: str = None, **kwargs) -> Project`

Creates a new project.

**Parameters:**
- `name` (str): Project name
- `description` (str): Project description
- `template_name` (str): Template to use
- `**kwargs`: Additional project parameters

**Returns:**
- `Project`: Created project instance

**Example:**
```python
from codomyrmex.project_orchestration import get_project_manager

manager = get_project_manager()

project = manager.create_project(
    name="my_project",
    description="A test project",
    template_name="ai_analysis",
    path="/path/to/project"
)
```

#### `get_project(name: str) -> Optional[Project]`

Gets a project by name.

**Parameters:**
- `name` (str): Project name

**Returns:**
- `Optional[Project]`: Project instance or None if not found

#### `list_projects(status: Optional[ProjectStatus] = None) -> List[str]`

Lists projects, optionally filtered by status.

**Parameters:**
- `status` (Optional[ProjectStatus]): Filter by project status

**Returns:**
- `List[str]`: List of project names

#### `update_project(name: str, **kwargs) -> Optional[Project]`

Updates a project.

**Parameters:**
- `name` (str): Project name
- `**kwargs`: Fields to update

**Returns:**
- `Optional[Project]`: Updated project instance or None if not found

**Example:**
```python
updated_project = manager.update_project(
    "my_project",
    description="Updated description",
    status=ProjectStatus.ACTIVE,
    metadata={"key": "value"}
)
```

#### `delete_project(name: str) -> bool`

Deletes a project.

**Parameters:**
- `name` (str): Project name

**Returns:**
- `bool`: True if project was deleted

#### `create_template(template: ProjectTemplate) -> bool`

Creates a new project template.

**Parameters:**
- `template` (ProjectTemplate): Template to create

**Returns:**
- `bool`: True if template was created

**Example:**
```python
from codomyrmex.project_orchestration import ProjectTemplate, ProjectType

template = ProjectTemplate(
    name="custom_template",
    project_type=ProjectType.WEB_APPLICATION,
    description="Custom web application template",
    directory_structure=["src/", "static/", "templates/"],
    files_to_create=["README.md", "requirements.txt"],
    dependencies=["flask", "jinja2"],
    workflows=["build", "deploy"]
)

success = manager.create_template(template)
```

---

## ResourceManager

The `ResourceManager` class manages resource allocation, deallocation, and usage monitoring.

### Class Definition

```python
class ResourceManager:
    def __init__(self)
```

### Methods

#### `add_resource(resource: Resource) -> bool`

Adds a resource to the manager.

**Parameters:**
- `resource` (Resource): Resource to add

**Returns:**
- `bool`: True if resource was added

**Example:**
```python
from codomyrmex.project_orchestration import get_resource_manager, Resource, ResourceType

manager = get_resource_manager()

resource = Resource(
    id="cpu_1",
    name="CPU Core 1",
    resource_type=ResourceType.CPU,
    capacity=100.0,
    unit="cores"
)

success = manager.add_resource(resource)
```

#### `get_resource(resource_id: str) -> Optional[Resource]`

Gets a resource by ID.

**Parameters:**
- `resource_id` (str): Resource ID

**Returns:**
- `Optional[Resource]`: Resource instance or None if not found

#### `list_resources(resource_type: Optional[ResourceType] = None) -> List[Resource]`

Lists resources, optionally filtered by type.

**Parameters:**
- `resource_type` (Optional[ResourceType]): Filter by resource type

**Returns:**
- `List[Resource]`: List of resources

#### `allocate_resource(resource_id: str, task_id: str, amount: float) -> Optional[ResourceAllocation]`

Allocates a resource for a task.

**Parameters:**
- `resource_id` (str): Resource ID
- `task_id` (str): Task ID
- `amount` (float): Amount to allocate

**Returns:**
- `Optional[ResourceAllocation]`: Allocation instance or None if failed

**Example:**
```python
allocation = manager.allocate_resource("cpu_1", "task_1", 50.0)
if allocation:
    print(f"Allocated {allocation.allocated_amount} of {allocation.resource_id}")
```

#### `release_resource(task_id: str, resource_id: str) -> bool`

Releases a resource allocation.

**Parameters:**
- `task_id` (str): Task ID
- `resource_id` (str): Resource ID

**Returns:**
- `bool`: True if resource was released

#### `get_available_capacity(resource_id: str) -> float`

Gets available capacity for a resource.

**Parameters:**
- `resource_id` (str): Resource ID

**Returns:**
- `float`: Available capacity

#### `get_resource_usage(resource_id: str) -> Optional[ResourceUsage]`

Gets resource usage statistics.

**Parameters:**
- `resource_id` (str): Resource ID

**Returns:**
- `Optional[ResourceUsage]`: Usage statistics or None if not found

#### `get_resource_summary() -> Dict[str, Any]`

Gets comprehensive resource summary.

**Returns:**
- `Dict[str, Any]`: Resource summary with statistics

---

## OrchestrationEngine

The `OrchestrationEngine` class coordinates all orchestration components.

### Class Definition

```python
class OrchestrationEngine:
    def __init__(self, config_dir: Optional[Path] = None, enable_performance_monitoring: bool = True)
```

### Methods

#### `create_session(name: str, description: str = "", metadata: Dict[str, Any] = None) -> OrchestrationSession`

Creates a new orchestration session.

**Parameters:**
- `name` (str): Session name
- `description` (str): Session description
- `metadata` (Dict[str, Any]): Session metadata

**Returns:**
- `OrchestrationSession`: Created session instance

**Example:**
```python
from codomyrmex.project_orchestration import get_orchestration_engine

engine = get_orchestration_engine()

session = engine.create_session(
    name="My Session",
    description="A test orchestration session",
    metadata={"project": "test_project"}
)
```

#### `get_session(session_id: str) -> Optional[OrchestrationSession]`

Gets a session by ID.

**Parameters:**
- `session_id` (str): Session ID

**Returns:**
- `Optional[OrchestrationSession]`: Session instance or None if not found

#### `list_sessions(status: Optional[SessionStatus] = None) -> List[OrchestrationSession]`

Lists sessions, optionally filtered by status.

**Parameters:**
- `status` (Optional[SessionStatus]): Filter by session status

**Returns:**
- `List[OrchestrationSession]`: List of sessions

#### `update_session(session_id: str, **kwargs) -> Optional[OrchestrationSession]`

Updates a session.

**Parameters:**
- `session_id` (str): Session ID
- `**kwargs`: Fields to update

**Returns:**
- `Optional[OrchestrationSession]`: Updated session instance or None if not found

#### `delete_session(session_id: str) -> bool`

Deletes a session.

**Parameters:**
- `session_id` (str): Session ID

**Returns:**
- `bool`: True if session was deleted

#### `execute_workflow_in_session(session_id: str, workflow_name: str) -> bool`

Executes a workflow in a session.

**Parameters:**
- `session_id` (str): Session ID
- `workflow_name` (str): Workflow name

**Returns:**
- `bool`: True if workflow was executed

#### `add_task_to_session(session_id: str, task: Task) -> bool`

Adds a task to a session.

**Parameters:**
- `session_id` (str): Session ID
- `task` (Task): Task to add

**Returns:**
- `bool`: True if task was added

#### `create_project_in_session(session_id: str, name: str, description: str = "") -> Optional[Project]`

Creates a project in a session.

**Parameters:**
- `session_id` (str): Session ID
- `name` (str): Project name
- `description` (str): Project description

**Returns:**
- `Optional[Project]`: Created project instance or None if failed

#### `allocate_resources_for_session(session_id: str, resource_id: str, amount: float) -> bool`

Allocates resources for a session.

**Parameters:**
- `session_id` (str): Session ID
- `resource_id` (str): Resource ID
- `amount` (float): Amount to allocate

**Returns:**
- `bool`: True if resources were allocated

#### `get_system_status() -> Dict[str, Any]`

Gets comprehensive system status.

**Returns:**
- `Dict[str, Any]`: System status with statistics

#### `get_health_status() -> Dict[str, Any]`

Gets system health status.

**Returns:**
- `Dict[str, Any]`: Health status for all components

---

## Data Classes

### WorkflowStep

Represents a single step in a workflow.

```python
@dataclass
class WorkflowStep:
    name: str
    module: str
    action: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list)
    timeout: Optional[int] = None
    retry_count: int = 0
    max_retries: int = 3
```

### WorkflowExecution

Tracks workflow execution state and results.

```python
@dataclass
class WorkflowExecution:
    workflow_name: str
    status: WorkflowStatus = WorkflowStatus.PENDING
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    results: Dict[str, Any] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    performance_metrics: Dict[str, Any] = field(default_factory=dict)
```

### Task

Represents an individual task in the orchestration system.

```python
@dataclass
class Task:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    module: str = ""
    action: str = ""
    parameters: Dict[str, Any] = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list)
    priority: TaskPriority = TaskPriority.NORMAL
    resources: List[TaskResource] = field(default_factory=list)
    timeout: Optional[int] = None
    max_retries: int = 3
    retry_delay: float = 1.0
    status: TaskStatus = TaskStatus.PENDING
    retry_count: int = 0
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Optional[TaskResult] = None
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
```

### Project

Represents a project in the orchestration system.

```python
@dataclass
class Project:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    project_type: ProjectType = ProjectType.GENERAL
    status: ProjectStatus = ProjectStatus.PLANNING
    path: Optional[str] = None
    template_name: Optional[str] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = None
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
```

### Resource

Represents a resource in the orchestration system.

```python
@dataclass
class Resource:
    id: str
    name: str
    resource_type: ResourceType
    capacity: float
    unit: str = "units"
    status: ResourceStatus = ResourceStatus.AVAILABLE
    metadata: Dict[str, Any] = field(default_factory=dict)
```

---

## Integration Examples

### Complete Workflow Example

```python
import asyncio
from codomyrmex.project_orchestration import (
    get_orchestration_engine,
    get_workflow_manager,
    WorkflowStep,
    Task,
    TaskPriority,
    Resource,
    ResourceType
)

async def complete_workflow_example():
    # Get orchestration engine
    engine = get_orchestration_engine()
    
    # Create session
    session = engine.create_session(
        name="Complete Workflow Example",
        description="Demonstrates complete orchestration workflow"
    )
    
    # Add resources
    cpu_resource = Resource(
        id="cpu_1",
        name="CPU Core 1",
        resource_type=ResourceType.CPU,
        capacity=100.0
    )
    engine.resource_manager.add_resource(cpu_resource)
    
    # Allocate resources for session
    engine.allocate_resources_for_session(session.session_id, "cpu_1", 50.0)
    
    # Create workflow
    steps = [
        WorkflowStep(
            name="setup",
            module="environment_setup",
            action="check_environment"
        ),
        WorkflowStep(
            name="analyze",
            module="static_analysis",
            action="analyze_code",
            dependencies=["setup"]
        ),
        WorkflowStep(
            name="visualize",
            module="data_visualization",
            action="create_chart",
            dependencies=["analyze"]
        )
    ]
    
    engine.workflow_manager.create_workflow("complete_workflow", steps)
    
    # Execute workflow
    result = engine.execute_workflow_in_session(session.session_id, "complete_workflow")
    print(f"Workflow execution result: {result}")
    
    # Add tasks to session
    task1 = Task(
        name="session_task1",
        module="module1",
        action="action1",
        priority=TaskPriority.HIGH
    )
    
    task2 = Task(
        name="session_task2",
        module="module2",
        action="action2",
        dependencies=["session_task1"],
        priority=TaskPriority.NORMAL
    )
    
    engine.add_task_to_session(session.session_id, task1)
    engine.add_task_to_session(session.session_id, task2)
    
    # Create project in session
    project = engine.create_project_in_session(
        session.session_id,
        "example_project",
        "Example project for orchestration"
    )
    
    # Get system status
    status = engine.get_system_status()
    print(f"System status: {status}")
    
    # Get health status
    health = engine.get_health_status()
    print(f"Health status: {health}")
    
    # Cleanup session
    engine.cleanup_session(session.session_id)
    
    # Shutdown engine
    engine.shutdown()

# Run the example
asyncio.run(complete_workflow_example())
```

### Resource Management Example

```python
from codomyrmex.project_orchestration import (
    get_resource_manager,
    get_task_orchestrator,
    Resource,
    ResourceType,
    Task,
    TaskResource
)

def resource_management_example():
    # Get managers
    resource_manager = get_resource_manager()
    task_orchestrator = get_task_orchestrator()
    
    # Add resources
    cpu_resource = Resource(
        id="cpu_1",
        name="CPU Core 1",
        resource_type=ResourceType.CPU,
        capacity=100.0
    )
    
    mem_resource = Resource(
        id="mem_1",
        name="Memory 1",
        resource_type=ResourceType.MEMORY,
        capacity=1024.0
    )
    
    resource_manager.add_resource(cpu_resource)
    resource_manager.add_resource(mem_resource)
    
    # Create tasks with resource requirements
    task1 = Task(
        name="cpu_intensive_task",
        module="module1",
        action="action1",
        resources=[
            TaskResource(type=ResourceType.CPU, identifier="cpu_1", mode="exclusive")
        ]
    )
    
    task2 = Task(
        name="memory_intensive_task",
        module="module2",
        action="action2",
        resources=[
            TaskResource(type=ResourceType.MEMORY, identifier="mem_1", mode="exclusive")
        ]
    )
    
    # Add tasks to orchestrator
    task_orchestrator.add_task(task1)
    task_orchestrator.add_task(task2)
    
    # Start execution
    task_orchestrator.start_execution()
    
    # Wait for tasks to complete
    time.sleep(2)
    
    # Stop execution
    task_orchestrator.stop_execution()
    
    # Get resource usage
    cpu_usage = resource_manager.get_resource_usage("cpu_1")
    mem_usage = resource_manager.get_resource_usage("mem_1")
    
    print(f"CPU usage: {cpu_usage.current_usage if cpu_usage else 0}")
    print(f"Memory usage: {mem_usage.current_usage if mem_usage else 0}")
    
    # Get resource summary
    summary = resource_manager.get_resource_summary()
    print(f"Resource summary: {summary}")

# Run the example
resource_management_example()
```

This comprehensive API documentation provides complete coverage of all classes, methods, and usage examples for the Codomyrmex Project Orchestration system.
