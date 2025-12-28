# Codomyrmex Agents — src/codomyrmex/project_orchestration

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: December 2025

## Purpose

Core module providing project management and workflow orchestration capabilities for the Codomyrmex platform. This module enables the coordination and automation of complex project workflows, integrating multiple Codomyrmex modules into cohesive, manageable processes.

The project_orchestration module serves as the central coordinator for multi-step operations, enabling users to define, execute, and monitor complex workflows that span multiple modules and systems.

## Module Overview

### Key Capabilities
- **Workflow Definition**: Create and manage complex multi-step workflows
- **Task Orchestration**: Coordinate individual tasks with dependencies
- **Project Management**: High-level project lifecycle management
- **Resource Allocation**: Manage shared resources and dependencies
- **Progress Tracking**: Monitor workflow execution and status
- **Parallel Execution**: Support concurrent task execution
- **Error Recovery**: Handle failures and recovery mechanisms

### Key Features
- Integration with all Codomyrmex modules for comprehensive workflows
- Template-based project scaffolding with automatic documentation
- Real-time progress monitoring and reporting
- Resource management and allocation tracking
- Error handling and recovery mechanisms
- Parallel and sequential execution modes

## Function Signatures

### Workflow Management Classes

```python
class WorkflowManager:
    """Manages workflow definitions and execution."""

    def __init__(self, config: dict = None) -> None
    def create_workflow(self, definition: dict) -> str
    def execute_workflow(self, workflow_id: str, context: dict = None) -> WorkflowExecution
    def get_workflow_status(self, workflow_id: str) -> WorkflowStatus
    def cancel_workflow(self, workflow_id: str) -> bool
    def list_workflows(self) -> list[dict]
    def validate_workflow(self, definition: dict) -> list[str]
```

### Task Orchestration Classes

```python
class TaskOrchestrator:
    """Coordinates individual tasks and dependencies."""

    def __init__(self, max_workers: int = 4) -> None
    def add_task(self, task: Task) -> str
    def execute_task(self, task_id: str) -> TaskResult
    def execute_parallel(self, task_ids: list[str]) -> list[TaskResult]
    def get_task_status(self, task_id: str) -> TaskStatus
    def cancel_task(self, task_id: str) -> bool
    def get_dependencies(self, task_id: str) -> list[str]
```

### Project Management Classes

```python
class ProjectManager:
    """High-level project lifecycle management."""

    def __init__(self, base_path: str = None) -> None
    def create_project(self, name: str, template: str = None) -> Project
    def load_project(self, path: str) -> Project
    def save_project(self, project: Project) -> bool
    def get_project_status(self, project: Project) -> ProjectStatus
    def archive_project(self, project: Project) -> bool
    def list_projects(self) -> list[Project]
```

### Resource Management Classes

```python
class ResourceManager:
    """Manages shared resources and dependencies."""

    def __init__(self) -> None
    def allocate_resource(self, resource_type: ResourceType, amount: int = 1) -> ResourceAllocation
    def release_resource(self, allocation: ResourceAllocation) -> bool
    def get_resource_usage(self) -> dict[ResourceType, ResourceUsage]
    def check_availability(self, resource_type: ResourceType, amount: int = 1) -> bool
    def monitor_resources(self) -> Iterator[dict]
```

### Data Classes

```python
@dataclass
class WorkflowStep:
    """Represents a single step in a workflow."""
    name: str
    action: str
    parameters: dict = field(default_factory=dict)
    dependencies: list[str] = field(default_factory=list)
    timeout: int = 300

@dataclass
class Task:
    """Represents a task to be executed."""
    name: str
    action: str
    priority: TaskPriority = TaskPriority.NORMAL
    parameters: dict = field(default_factory=dict)
    resources: list[TaskResource] = field(default_factory=list)
    timeout: int = 300

@dataclass
class Project:
    """Represents a project configuration."""
    name: str
    path: str
    template: ProjectTemplate
    workflows: list[str] = field(default_factory=list)
    resources: list[Resource] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)
```

### Enums

```python
class WorkflowStatus(Enum):
    """Workflow execution states."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class TaskStatus(Enum):
    """Task execution states."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class TaskPriority(Enum):
    """Task execution priorities."""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"

class ProjectStatus(Enum):
    """Project lifecycle states."""
    CREATED = "created"
    ACTIVE = "active"
    COMPLETED = "completed"
    ARCHIVED = "archived"
    FAILED = "failed"
```

## Active Components

### Core Implementation
- `__init__.py` – Module initialization and public API exports
- `workflow_manager.py` – Workflow definition and execution management
- `task_orchestrator.py` – Task coordination and dependency management
- `project_manager.py` – Project lifecycle management
- `resource_manager.py` – Resource allocation and monitoring
- `orchestration_engine.py` – Core orchestration logic and execution
- `documentation_generator.py` – Automatic documentation generation for projects
- `mcp_tools.py` – Model Context Protocol integration tools

### Templates and Scaffolding
- `templates/` – Project templates and scaffolding components

### Documentation
- `README.md` – Module usage and overview
- `API_SPECIFICATION.md` – Complete API documentation
- `USAGE_EXAMPLES.md` – Practical usage demonstrations
- `DEVELOPER_GUIDE.md` – Development and integration guide
- `COMPREHENSIVE_API_DOCUMENTATION.md` – Detailed API reference
- `MCP_TOOL_SPECIFICATION.md` – AI agent tool specifications
- `SECURITY.md` – Security considerations for orchestration
- `CHANGELOG.md` – Version history and updates

### Supporting Files
- `requirements.txt` – Module dependencies
- `tests/` – Comprehensive test suite

## Operating Contracts

### Universal Orchestration Protocols

All workflow orchestration within the Codomyrmex platform must:

1. **Maintain Workflow Integrity** - Ensure workflows execute completely or rollback safely
2. **Handle Dependencies** - Properly resolve and manage task dependencies
3. **Resource Safety** - Prevent resource conflicts and ensure proper cleanup
4. **Error Containment** - Isolate failures and provide recovery mechanisms
5. **Progress Transparency** - Provide clear status and progress information

### Module-Specific Guidelines

#### Workflow Definition
- Support complex dependency graphs with proper validation
- Allow parameterization of workflow steps
- Provide clear error messages for invalid definitions
- Support workflow templates and reuse

#### Task Execution
- Execute tasks in dependency order when possible
- Support parallel execution for independent tasks
- Provide timeout mechanisms for runaway tasks
- Implement proper error handling and recovery

#### Resource Management
- Track resource usage and prevent over-allocation
- Support different resource types (CPU, memory, network, etc.)
- Provide monitoring and alerting for resource issues
- Ensure proper cleanup on task completion or failure

## Navigation Links

### Module Documentation
- **Module Overview**: [README.md](README.md) - Complete module documentation
- **API Reference**: [API_SPECIFICATION.md](API_SPECIFICATION.md) - Detailed API specification
- **Usage Examples**: [USAGE_EXAMPLES.md](USAGE_EXAMPLES.md) - Practical usage demonstrations
- **Developer Guide**: [DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md) - Development and integration guide

### Related Modules

### Platform Navigation
- **Parent Directory**: [codomyrmex](../README.md) - Package overview
- **Project Root**: [README](../../../README.md) - Main project documentation

## Agent Coordination

### Integration Points

When integrating with other modules:

1. **Workflow Integration** - Define workflows that span multiple modules
2. **Resource Coordination** - Coordinate resource usage across module operations
3. **Status Propagation** - Share execution status and progress information
4. **Error Handling** - Provide consistent error handling across workflows

### Quality Gates

Before orchestration changes are accepted:

1. **Workflow Validation Tested** - All workflow definitions properly validated
2. **Dependency Resolution Verified** - Task dependencies resolved correctly
3. **Resource Management Tested** - Resource allocation and cleanup work properly
4. **Error Recovery Validated** - Failed workflows can be safely recovered or rolled back
5. **Performance Optimized** - Orchestration overhead remains within acceptable limits

## Version History

- **v0.1.0** (December 2025) - Initial workflow orchestration system with task management, resource allocation, and project coordination capabilities
