# Codomyrmex Agents — src/codomyrmex/project_orchestration

## Signposting
- **Parent**: [codomyrmex](../AGENTS.md)
- **Self**: [Agents](AGENTS.md)
- **Children**:
    - [templates](templates/AGENTS.md)
    - [tests](tests/AGENTS.md)
- **Key Artifacts**:
    - [Functional Spec](SPEC.md)
    - [Human Readme](README.md)

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Purpose
Project management and task orchestration capabilities integrating Codomyrmex modules into cohesive workflows. Provides task and workflow management, inter-module coordination, project templates and scaffolding with automatic documentation generation, progress tracking and reporting, resource management, parallel execution support, and error handling and recovery.

## Active Components
- `API_SPECIFICATION.md` – Detailed API specification
- `CHANGELOG.md` – Version history
- `COMPREHENSIVE_API_DOCUMENTATION.md` – Complete API documentation
- `DEVELOPER_GUIDE.md` – Developer guide
- `MCP_TOOL_SPECIFICATION.md` – MCP tool specification
- `README.md` – Project file
- `SECURITY.md` – Security considerations
- `SPEC.md` – Project file
- `USAGE_EXAMPLES.md` – Usage examples
- `__init__.py` – Module exports and public API
- `documentation_generator.py` – Generates README.md and AGENTS.md files for projects
- `mcp_tools.py` – MCP tools for AI-driven orchestration
- `orchestration_engine.py` – Main orchestration engine coordinating all components
- `parallel_executor.py` – Parallel execution support
- `project_manager.py` – High-level project lifecycle management
- `resource_manager.py` – Manages shared resources and dependencies
- `task_orchestrator.py` – Coordinates individual tasks and dependencies
- `templates/` – Directory containing project templates
- `tests/` – Directory containing tests components
- `workflow_dag.py` – Workflow DAG (Directed Acyclic Graph) implementation
- `workflow_manager.py` – Manages workflow definitions and execution

## Key Classes and Functions

### OrchestrationEngine (`orchestration_engine.py`)
- `OrchestrationEngine(config: Optional[dict[str, Any]] = None)` – Main orchestration engine coordinating all components
- `create_session(user_id: str = "system", **kwargs) -> str` – Create a new orchestration session for context management
- `execute_workflow(workflow_name: str, session_id: Optional[str] = None, **params) -> Dict[str, Any]` – Execute a workflow with orchestration management
- `register_event_handler(event: str, handler: Callable) -> None` – Register an event handler
- `emit_event(event: str, data: dict[str, Any]) -> None` – Emit an event to registered handlers

### OrchestrationSession (`orchestration_engine.py`)
- `OrchestrationSession` (dataclass) – Orchestration session context:
  - `session_id: str` – Unique session identifier
  - `user_id: str` – User identifier
  - `status: SessionStatus` – Session status
  - `mode: OrchestrationMode` – Execution mode (SEQUENTIAL, PARALLEL, PRIORITY, RESOURCE_AWARE)
  - `created_at: datetime` – Creation timestamp
  - `metadata: dict[str, Any]` – Additional metadata

### WorkflowManager (`workflow_manager.py`)
- `WorkflowManager(config_dir: Optional[str] = None)` – Manages workflow definitions and execution
- `create_workflow(name: str, steps: List[WorkflowStep]) -> bool` – Create a new workflow
- `execute_workflow(name: str, context: Optional[dict] = None) -> WorkflowExecution` – Execute a workflow
- `get_workflow(name: str) -> Optional[dict]` – Get workflow definition

### TaskOrchestrator (`task_orchestrator.py`)
- `TaskOrchestrator(max_workers: int = 4)` – Coordinates individual tasks and dependencies
- `add_task(task: Task) -> str` – Add a task to the orchestrator
- `execute_task(task_id: str) -> TaskResult` – Execute a specific task
- `start_execution() -> None` – Start task execution in background
- `stop_execution() -> None` – Stop task execution

### ProjectManager (`project_manager.py`)
- `ProjectManager(projects_dir: Optional[str] = None, templates_dir: Optional[str] = None)` – High-level project lifecycle management
- `create_project(name: str, project_type: ProjectType, template: Optional[ProjectTemplate] = None) -> Project` – Create a new project
- `get_project(project_id: str) -> Optional[Project]` – Get project by ID
- `list_projects() -> List[Project]` – List all projects

### ResourceManager (`resource_manager.py`)
- `ResourceManager(config_file: Optional[str] = None)` – Manages shared resources and dependencies
- `allocate_resource(resource_type: ResourceType, requirements: dict) -> ResourceAllocation` – Allocate a resource
- `release_resource(allocation_id: str) -> bool` – Release a resource allocation
- `get_resource_status(resource_id: str) -> ResourceStatus` – Get resource status

### DocumentationGenerator (`documentation_generator.py`)
- `DocumentationGenerator()` – Generates README.md and AGENTS.md files for projects and nested directories
- `generate_project_docs(project_path: str) -> None` – Generate documentation for a project

### Task (`task_orchestrator.py`)
- `Task` (dataclass) – Task data structure:
  - `task_id: str` – Unique task identifier
  - `name: str` – Task name
  - `module: str` – Module to execute
  - `action: str` – Action to perform
  - `parameters: dict[str, Any]` – Task parameters
  - `status: TaskStatus` – Current task status
  - `priority: TaskPriority` – Task priority
  - `dependencies: List[str]` – Task dependencies (task IDs)

### TaskStatus (`task_orchestrator.py`)
- `TaskStatus` (Enum) – Task status: PENDING, RUNNING, COMPLETED, FAILED, CANCELLED, SKIPPED

### TaskPriority (`task_orchestrator.py`)
- `TaskPriority` (Enum) – Task priority levels

### Module Functions (`__init__.py`)
- `create_workflow_steps(name: str, steps: list) -> bool` – Create a new workflow with steps
- `create_task(name: str, module: str, action: str, **kwargs) -> Task` – Create a new task instance
- `get_mcp_tools() -> List[dict]` – Get available MCP tools
- `get_mcp_tool_definitions() -> dict` – Get MCP tool definitions
- `execute_mcp_tool(tool_name: str, parameters: dict) -> MCPToolResult` – Execute an MCP tool

## Operating Contracts
- Maintain alignment between code, documentation, and configured workflows.
- Ensure Model Context Protocol interfaces remain available for sibling agents.
- Record outcomes in shared telemetry and update TODO queues when necessary.

## Navigation Links
- **Human Documentation**: [README.md](README.md)
- **Functional Specification**: [SPEC.md](SPEC.md)
- **📁 Parent Directory**: [codomyrmex](../README.md) - Parent directory documentation
- **🏠 Project Root**: [README](../../../README.md) - Main project documentation