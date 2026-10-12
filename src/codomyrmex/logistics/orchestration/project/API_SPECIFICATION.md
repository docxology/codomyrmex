# Project Orchestration - API Specification

## Introduction

This API specification documents the programmatic interfaces for the Project Orchestration module of Codomyrmex. The module provides project management, workflow orchestration, and task coordination through a set of Python classes and functions. All execution APIs are synchronous.

## Task Dispatch

Tasks and workflow steps name the code they run with `module` and `action`. The callable is resolved as follows and called with the task's parameters as keyword arguments (`action(**parameters)`):

1. An explicit registration made with `TaskOrchestrator.register_action(module, action, func)` (stored in the orchestrator's `ActionRegistry`).
2. Otherwise the module `codomyrmex.<module>` is imported and its public attribute `<action>` is used. `module` may be dotted (for example `"coding.static_analysis"`); `action` must be a public attribute name.

If the callable returns an awaitable it is run to completion in the worker thread. An unknown or malformed module or action, or an exception raised by the callable, fails the task: its `TaskResult.status` is `FAILED` and `TaskResult.error` holds the reason. No task is reported as completed unless its callable actually ran and returned.

```python
from codomyrmex.logistics.orchestration.project import Task, get_task_orchestrator

orchestrator = get_task_orchestrator()
orchestrator.register_action("reports", "summarise", lambda text: text[:80])

result = orchestrator.execute_task(
    Task(name="summary", module="reports", action="summarise", parameters={"text": "..."})
)
print(result.status, result.result, result.error)
```

## Core Classes and Interfaces

### OrchestrationEngine

The main coordination engine that manages all orchestration operations.

#### OrchestrationEngine Methods

##### `OrchestrationEngine(config: Optional[Dict[str, Any]] = None, *, workflow_manager=None, task_orchestrator=None, project_manager=None, resource_manager=None)`

- **Description**: Creates an engine. Components that are not passed in are created from `config` and wired together: the task orchestrator allocates from the engine's resource manager and the workflow manager runs steps on the engine's task orchestrator. `shutdown()` stops the task orchestrator only if the engine created it.
- **Config keys**: `workflows_dir`, `projects_dir`, `max_workers`.
- **Note**: `get_orchestration_engine()` returns a global engine built on the global `get_workflow_manager()`, `get_task_orchestrator()`, `get_project_manager()` and `get_resource_manager()` singletons.

##### `create_session(user_id: str = "system", **kwargs) -> str`

- **Description**: Creates a new orchestration session for context management.
- **Parameters**:
    - `user_id` (string): User identifier for the session. Default: "system"
    - `mode` (string, optional): Execution mode. One of: "sequential", "parallel", "priority", "resource_aware". Default: "resource_aware"
    - `max_parallel_tasks` (int, optional): Maximum concurrent tasks. Default: 4
    - `max_parallel_workflows` (int, optional): Maximum concurrent workflows. Default: 2
    - `timeout_seconds` (int, optional): Session timeout in seconds; bounds `execute_task` and `execute_complex_workflow`
    - `resource_requirements` (dict, optional): Resources allocated for the duration of each `execute_workflow` call
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

##### `execute_workflow(workflow_name: str, session_id: Optional[str] = None, **params) -> Dict[str, Any]`

- **Description**: Runs a registered workflow through `WorkflowManager.execute_workflow` and returns once every step has finished. The session status becomes `COMPLETED` or `FAILED` and a `workflow_completed` event is emitted.
- **Parameters**:
    - `workflow_name` (string): Name of the workflow to execute
    - `session_id` (Optional[str]): Session ID for context (creates new if not provided)
    - `**params`: Workflow-level parameters merged over every step's parameters
- **Returns**: Dictionary with execution results:

  ```python
  {
    "success": bool,          # True only if every required step completed
    "status": str,            # "completed" or "failed"
    "execution_id": str,
    "result": dict,           # step name -> TaskResult.to_dict()
    "error": Optional[str],   # failed steps and their errors
    "execution_time": float,  # seconds
    "steps_executed": int     # steps whose action actually started
  }
  ```

- **Errors**: Never raises for workflow problems. An unknown session, unknown workflow, invalid dependencies (missing step, cycle, duplicate name), unsupported `run_if` condition or failed resource allocation returns `{"success": False, "error": ...}`.
- **Example**:

  ```python
  result = engine.execute_workflow("ai-analysis", code_path="./src")
  if result["success"]:
      print(f"Workflow completed: {result['steps_executed']} steps")
  else:
      print(f"Workflow failed: {result['error']}")
  ```

##### `execute_task(task: Union[Task, Dict[str, Any]], session_id: Optional[str] = None) -> Dict[str, Any]`

- **Description**: Execute a single task and wait for it to finish. Dependencies on task IDs the orchestrator does not know fail immediately. If the session has `timeout_seconds` and the task does not finish in time, it is cancelled and a failure is returned.
- **Parameters**:
    - `task` (Union[Task, Dict[str, Any]]): Task object or task dictionary
    - `session_id` (Optional[str]): Session ID (creates new if not provided)
- **Returns**: Dictionary with execution results:

  ```python
  {
    "success": bool,
    "result": Optional[dict],  # TaskResult.to_dict()
    "error": Optional[str],
    "task_id": str
  }
  ```

##### `execute_project_workflow(project_name: str, workflow_name: str, session_id: Optional[str] = None, **params) -> Dict[str, Any]`

- **Description**: Execute a workflow for a project registered with the engine's `ProjectManager`. The run goes through `execute_workflow` (`params` are passed to the steps unchanged) and is recorded in the project's metrics: `workflow_executions`, `successful_workflow_executions`, `last_workflow`, `last_workflow_success`, `last_workflow_execution`.
- **Parameters**:
    - `project_name` (string): Project name
    - `workflow_name` (string): Workflow to execute
    - `session_id` (Optional[str]): Session ID (creates new if not provided)
    - `**params`: Workflow parameters
- **Returns**: The `execute_workflow` result plus `project_name`; `{"success": False, "error": "Project <name> not found"}` for an unknown project.

##### `create_project_from_workflow(project_name: str, workflow_name: str, template_name: str = "ai_analysis", description: str = "", session_id: Optional[str] = None, **params) -> Dict[str, Any]`

- **Description**: Create a project and run a workflow for it. `template_name` is a `ProjectType` value. A successful run adds a `workflow_<name>_completed` milestone to the project.
- **Returns**:

  ```python
  {
    "success": bool,           # the workflow outcome
    "project_created": bool,
    "project": dict,           # Project.to_dict(), when created
    "workflow_result": dict,   # execute_project_workflow result
    "error": Optional[str]
  }
  ```

##### `execute_complex_workflow(workflow_definition: Dict[str, Any], session_id: Optional[str] = None) -> Dict[str, Any]`

- **Description**: Execute an ad-hoc workflow definition with interdependent steps. Steps are built from `steps` (each with `name`, `module`, `action`, optional `parameters` and `dependencies`) plus the top-level `dependencies` mapping, then run with `WorkflowManager.execute_steps` bounded by the session's `timeout_seconds`.
- **Parameters**:
    - `workflow_definition` (Dict[str, Any]): Definition with `steps` and optional `dependencies` and `name`
    - `session_id` (Optional[str]): Session ID (creates new if not provided)
- **Returns**: Dictionary with execution results:

  ```python
  {
    "success": bool,                    # True only if every step completed
    "results": Dict[str, Any],          # step name -> TaskResult.to_dict()
    "execution_stats": Dict[str, Any],  # TaskOrchestrator.get_execution_stats()
    "error": Optional[str]              # failed steps, or the invalid-definition reason
  }
  ```

##### `get_session(session_id: str) -> Optional[OrchestrationSession]`

- **Description**: Get a session by ID.
- **Parameters**:
    - `session_id` (string): Session ID
- **Returns**: OrchestrationSession object or None if not found

##### `close_session(session_id: str) -> bool`

- **Description**: Close an orchestration session and cleanup resources.
- **Parameters**:
    - `session_id` (string): Session ID to close
- **Returns**: bool - True if session was closed, False if not found

##### `register_event_handler(event: str, handler: Callable)`

- **Description**: Register an event handler for orchestration events.
- **Parameters**:
    - `event` (string): Event name (e.g., "workflow_completed", "session_closed")
    - `handler` (Callable): Handler function that accepts (event: str, data: dict) arguments

##### `get_metrics() -> Dict[str, Any]`

- **Description**: Get metrics for all components.
- **Returns**: Dictionary with `timestamp`, `sessions` (`total`, `by_status` keyed by status value), `workflows` (`WorkflowManager.get_performance_summary()`), `tasks` (`TaskOrchestrator.get_execution_stats()`), `projects` (`ProjectManager.get_projects_summary()`) and `resources` (`ResourceManager.get_resource_usage()`)

##### `get_system_status() -> Dict[str, Any]`

- **Description**: Retrieves system status built from the components' real state.
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
      "running_workflows": int   # executions currently RUNNING
    },
    "task_orchestrator": {       # TaskOrchestrator.get_execution_stats()
      "total_tasks": int,
      "pending": int,
      "blocked": int,
      "running": int,
      "completed": int,
      "failed": int,
      "cancelled": int
    },
    "project_manager": dict,     # ProjectManager.get_projects_summary()
    "resource_manager": dict,    # ResourceManager.get_resource_usage()
    "performance": dict          # If available
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

#### WorkflowManager Methods

##### `WorkflowManager(persistence_dir: Optional[Path] = None, config_dir: Optional[Path] = None, task_orchestrator: Optional[TaskOrchestrator] = None)`

- **Description**: Loads every `*.json` workflow file in `config_dir` (default `config/workflows/production` under the current directory; created if missing, as is `persistence_dir`, default `.workflows`). Files that do not follow the workflow file format are logged and skipped; `workflow_files` maps each loaded workflow to its file. Steps run on `task_orchestrator` (default: the global one).
- **Workflow file format**:

  ```json
  {
    "name": "custom-analysis",
    "steps": [
      {
        "name": "analyze",
        "module": "coding.static_analysis",
        "action": "analyze_project",
        "parameters": {"project_root": "."},
        "dependencies": ["setup"],
        "timeout": null,
        "max_retries": 0,
        "required": true
      }
    ]
  }
  ```

  `name` defaults to the file stem and `steps` is required. Each step needs non-empty `name`, `module` and `action`; the other keys are optional (`max_retries` becomes `WorkflowStep.retry_count`). Other keys, such as a top-level `description`, are ignored. A step with `run_if` makes the file invalid. Parameters are passed verbatim; `{{step.output}}` substitution is not supported. If two files define the same name, the later file wins and a warning is logged.

##### `create_workflow(name: str, steps: List[WorkflowStep], *, persist: bool = False) -> bool`

- **Description**: Registers a workflow with the specified steps, replacing any workflow of the same name. With `persist=True` the workflow is also written with `save_workflow`, so managers created later (for example by another `codomyrmex` process) load it; if saving raises, the previous registration (or its absence) is restored and the error propagates.
- **Parameters**:
    - `name` (string): Workflow name.
    - `steps` (List[WorkflowStep]): Workflow steps. Their order does not matter; `dependencies` (step names) determine execution order.
    - `persist` (bool, keyword-only): Also save the workflow file. Default False (in memory only).
- **Returns**: bool - True.
- **Raises**: with `persist=True`, as `save_workflow`.
- **Example**:

  ```python
  from codomyrmex.logistics.orchestration.project import WorkflowManager, WorkflowStep

  manager = WorkflowManager()
  steps = [
      WorkflowStep(
          name="analyze",
          module="coding.static_analysis",
          action="analyze_project",
          parameters={"project_root": "."},
          dependencies=["setup"]
      ),
      WorkflowStep(name="setup", module="environment_setup", action="validate_environment"),
  ]
  manager.create_workflow("custom-analysis", steps, persist=True)
  # config/workflows/production/custom-analysis.json now exists
  ```

##### `save_workflow(name: str) -> Path`

- **Description**: Validates a registered workflow and writes it atomically in the workflow file format: back to the file it was loaded from, otherwise to `config_dir / f"{name}.json"`. Records the path in `workflow_files`.
- **Returns**: The path written.
- **Raises**:
    - `KeyError`: No workflow named `name` is registered.
    - `ValueError`: `name` cannot be a file name (it must start with a letter or digit and contain only letters, digits, `.`, `_`, `-`); a step is malformed; the dependencies are invalid (missing step, cycle, duplicate step name); or the target file exists and holds a different or unreadable workflow (it is not overwritten).
    - `NotImplementedError`: A step sets `run_if`.
    - `TypeError`: A step's parameters are not JSON-serialisable (`ValueError` for NaN/infinity).
    - `OSError`: The file cannot be written.

##### `execute_workflow(name: str, **params) -> WorkflowExecution`

- **Description**: Executes a registered workflow synchronously and returns the finished execution. `params` are merged over each step's `parameters`. Equivalent to `execute_steps(name, steps, params)`.
- **Raises**:
    - `ValueError`: If the workflow is not registered, or its dependencies are invalid (missing step, cycle, duplicate step name). Nothing runs in that case.
    - `NotImplementedError`: If a step sets `run_if` (conditions are not supported).
- **Example**:

  ```python
  from codomyrmex.logistics.orchestration.project import WorkflowStatus, get_workflow_manager

  execution = get_workflow_manager().execute_workflow("custom-analysis", path="./src")
  if execution.status == WorkflowStatus.COMPLETED:
      for step_name, step_result in execution.step_results.items():
          print(step_name, step_result["result"])
  else:
      print(f"Workflow failed: {execution.error}")
  ```

##### `execute_steps(workflow_name: str, steps: Sequence[WorkflowStep], params: Optional[Dict[str, Any]] = None, timeout: Optional[float] = None) -> WorkflowExecution`

- **Description**: Validates the steps, submits them to the task orchestrator in topological order of their dependencies, waits for all of them and returns the finished execution.
- **Semantics**:
    - Independent steps run concurrently; every dependency is enforced regardless of listing order.
    - A step whose dependency failed is failed without running; unrelated steps still run.
    - `status` is `COMPLETED` when every `required` step completed, otherwise `FAILED` with `error` listing each failed required step. `end_time` and `step_results` (step name to `TaskResult.to_dict()`) are always set.
    - If `timeout` expires, unfinished steps are cancelled and the execution fails.
- **Raises**: as `execute_workflow`.

##### `list_workflows() -> List[str]`

- **Description**: List the names of registered workflows. Use `get_workflow(name)` for a workflow's steps and `workflow_files[name]` for its definition file.

##### `get_performance_summary() -> Dict[str, Any]`

- **Description**: Aggregate execution statistics.
- **Returns**: `total_executions`, `successful_executions`, `failed_executions`, `running_executions`, `average_duration` (seconds).

---

### TaskOrchestrator

Coordinates individual task execution with dependency management. See [Task Dispatch](#task-dispatch) for how `module`/`action` are resolved.

#### TaskOrchestrator Methods

##### `TaskOrchestrator(max_workers: int = 4, resource_manager: Optional[ResourceManager] = None, actions: Optional[ActionRegistry] = None)`

- **Description**: Creates an orchestrator. `Task.resources` are allocated from `resource_manager` (default: the global one); `actions` holds explicit action registrations (default: a new, empty registry).

##### `register_action(module: str, action: str, func: Callable) -> None`

- **Description**: Register `func` as the implementation of `module`/`action`. Registrations take precedence over import-based resolution.

##### `submit_task(task: Task) -> str`

- **Description**: Add a task to the orchestrator. The task is queued when its dependencies (task IDs) have completed, blocked while they are pending or unknown, and failed immediately if one already failed or was cancelled.
- **Parameters**:
    - `task` (Task): Task object to add
- **Returns**: Task ID (string)
- **Example**:

  ```python
  task = Task(
      name="analyze_code",
      module="coding.static_analysis",
      action="analyze_project",
      parameters={"project_root": "./src"}
  )
  task_id = orchestrator.submit_task(task)
  ```

##### `execute_task(task: Task) -> TaskResult`

- **Description**: Submits a task and blocks until it reaches a final state.
- **Parameters**:
    - `task` (Task): Task object to execute
- **Returns**: The task's `TaskResult`:

  ```python
  TaskResult(
      task_id=str,
      status=TaskStatus,        # COMPLETED, FAILED or CANCELLED
      result=Any,               # the action's return value
      error=Optional[str],      # why the task failed or was cancelled
      start_time=Optional[datetime],
      end_time=Optional[datetime],
      duration=Optional[float],
      metadata=dict,            # e.g. {"allocations": [...]}
  )
  ```

  `TaskResult.success` is True only for `COMPLETED`.

##### `wait_for_tasks(task_ids: Iterable[str], timeout: Optional[float] = None) -> bool`

- **Description**: Block until every listed task has finished.
- **Returns**: True when all finished, False if `timeout` expired.
- **Raises**: `KeyError` for unknown task IDs; `TaskExecutionError` if processing was stopped while some of the tasks are still queued or blocked.

##### `start_processing()`

- **Description**: Start the background thread that processes tasks. `submit_task` starts it automatically.

##### `stop_execution()`

- **Description**: Stop the background thread (waits up to 2 seconds for it to exit). Tasks already running finish; queued tasks stay queued.

##### `wait_for_completion(timeout: Optional[float] = 10.0) -> bool`

- **Description**: Wait for all tasks known to the orchestrator to finish.
- **Returns**: bool - True if all tasks finished, False if timeout was reached.

##### `cancel_task(task_id: str) -> bool`

- **Description**: Cancel a task. A queued or blocked task is removed and never runs. A running task cannot be interrupted: it is marked `CANCELLED` immediately and its eventual return value is discarded. Dependents of a cancelled task fail.
- **Returns**: bool - True if the task was cancelled, False if not found or already finished

##### `get_task(task_id: str) -> Optional[Task]`

- **Description**: Get a task by ID.

##### `get_task_result(task_id: str) -> Optional[TaskResult]`

- **Description**: Get the result of a finished task, or None if it has not finished.

##### `list_tasks() -> List[Task]`

- **Description**: List all tasks.

##### `get_execution_stats() -> Dict[str, Any]`

- **Description**: Gets execution statistics.
- **Returns**: Statistics dictionary

  ```python
  {
    "total_tasks": int,
    "pending": int,     # PENDING or READY
    "blocked": int,
    "running": int,
    "completed": int,
    "failed": int,
    "cancelled": int
  }
  ```

#### Task Resources

`Task.resources` is a list of `TaskResource(resource_type, amount=1.0, resource_id=None)`. Immediately before a task runs, every requirement is allocated from the orchestrator's `ResourceManager` (all or nothing) and the allocations are released when the task finishes, fails or is cancelled.

- With `resource_id`, that resource is used; its type must equal `resource_type`.
- Without it, `resource_type` must be a `ResourceType` value and the matching resource with the most free capacity is used.
- A requirement that can never be met fails the task with a `TaskExecutionError` message: unknown type or resource ID, type mismatch, non-positive amount, amount above every candidate's capacity, or candidates that are `offline`, `maintenance`, `depleted` or `unknown`.
- A requirement that is only temporarily short of capacity keeps the task queued until capacity is released.

```python
from codomyrmex.logistics.orchestration.project import Task, TaskResource

task = Task(
    name="heavy_analysis",
    module="coding.static_analysis",
    action="analyze_project",
    parameters={"project_root": "./src"},
    resources=[TaskResource(resource_type="memory", amount=512)],
)
```

---

### ProjectManager

High-level project lifecycle management.

#### ProjectManager Methods

##### `ProjectManager(projects_root: Optional[Union[Path, str]] = None)`

- **Description**: `projects_root` (default: the current directory) is where new projects are created. Projects saved as `<projects_root>/*/project.json` are registered on construction. A file that cannot be read or is not a valid project is logged and skipped, as is a second file with an already loaded name. The directory containing `project.json` is the project's `path` (a different recorded path, e.g. after a move, is replaced with a warning).

##### `create_project(name: str, type: ProjectType, description: str = "", path: Optional[Path] = None) -> Optional[Project]`

- **Description**: Creates and scaffolds a project (`src/`, `tests/`, `config/`, `docs/` plus generated README/AGENTS docs), saves `<path>/project.json` and registers it. A project whose `path` is outside `projects_root` is saved, but only a manager rooted at that path's parent finds it again.
- **Parameters**:
    - `name` (string): Project name, unique within the manager
    - `type` (ProjectType): Project type
    - `description` (string, optional): Project description
    - `path` (Path, optional): Project directory; defaults to `projects_root / name`
- **Returns**: The `Project`, or None if the name is already registered, the directory already exists, or scaffolding (directory creation, documentation generation, saving `project.json`) failed; the reason is logged and a partially created directory is removed
- **Example**:

  ```python
  from codomyrmex.logistics.orchestration.project import ProjectManager, ProjectType

  manager = ProjectManager()
  project = manager.create_project(
      "web-app-analysis",
      ProjectType.WEB_APPLICATION,
      description="Analysis of web application code",
  )
  ```

##### `get_project(name: str) -> Optional[Project]` / `list_projects() -> List[Project]`

- **Description**: Look up one registered project, or list all of them.

##### `update_project_status(name: str, status: ProjectStatus) -> bool`

- **Description**: Transition the project's lifecycle status and save `project.json`. Returns False for an unknown project.

##### `update_project_metrics(name: str, metrics: Dict[str, Any]) -> bool`

- **Description**: Merge `metrics` into `Project.metrics` and save `project.json`. Returns False for an unknown project.

##### `add_project_milestone(name: str, milestone_name: str, milestone_data: Optional[Dict[str, Any]] = None) -> bool`

- **Description**: Record a milestone (its data plus a `recorded_at` timestamp) in `Project.milestones` and save `project.json`. Returns False for an unknown project.

The three update methods also set `updated_at`. They save a changed copy first and change the registered project only after the save succeeded: `TypeError` (value not JSON-serialisable), `ValueError` (NaN or infinity) and `OSError` (write failed) propagate and leave the project unchanged.

##### `save_project(name: str) -> Path`

- **Description**: Write a registered project's `project.json` (atomically) after changing the `Project` object directly. Returns the path.
- **Raises**: `KeyError` for an unknown project; `TypeError`, `ValueError` or `OSError` as above.

##### `get_projects_summary() -> Dict[str, Any]`

- **Description**: Summarise the registered projects.
- **Returns**:

  ```python
  {
    "total_projects": int,
    "by_status": Dict[str, int],   # keyed by ProjectStatus value
    "by_type": Dict[str, int],     # keyed by ProjectType value
    "recent_activity": List[dict]  # {"name", "status", "updated_at"}, newest first
  }
  ```

---

### ResourceManager

System resource allocation and management.

#### ResourceManager Methods

##### `allocate(resource_id: str, requester_id: str, amount: float = 1.0, timeout: Optional[float] = None) -> Optional[ResourceAllocation]`

- **Description**: Allocate `amount` of one resource. Returns None if the resource is unknown, not `available`/`allocated`, or short of capacity.

##### `release(allocation_id: str) -> bool`

- **Description**: Release an allocation and restore capacity. Returns False for an unknown allocation.

##### `allocate_resources(requester_id: str, requirements: Dict[str, Dict[str, Any]], timeout: Optional[float] = None) -> Optional[List[ResourceAllocation]]`

- **Description**: Allocates several resources at once. Keys `cpu` and `memory` map to `sys-compute` and `sys-memory`; any other key is used as a resource ID. The amount is taken from `cores`, `gb` or `amount` (default 1). All allocations are rolled back if any fails.
- **Returns**: The allocations, or None if any allocation failed.
- **Example**:

  ```python
  manager = ResourceManager()
  allocations = manager.allocate_resources(
      "task_123",
      {"cpu": {"cores": 2}, "memory": {"gb": 4}},
  )
  ```

##### `deallocate_resources(requester_id: str) -> bool`

- **Description**: Release every allocation held by `requester_id`.
- **Returns**: True if any allocation was released.

##### `get_usage(resource_id: str) -> Optional[ResourceUsage]`

- **Description**: Usage statistics for one resource (capacity, allocated and available amounts, allocation count, utilisation percentage).

##### `get_resource_usage() -> Dict[str, Any]`

- **Description**: System-wide usage summary.
- **Returns**:

  ```python
  {
    "total_resources": int,
    "total_allocations": int,       # currently active allocations
    "lifetime_allocations": int,    # allocations ever granted
    "resources_by_type": Dict[str, int],
    "utilization_summary": Dict[str, float],  # mean utilisation % by type
    "resources": Dict[str, dict]    # per resource: name, type, status, capacity,
                                    # allocated, available, allocation_count,
                                    # utilization_percentage
  }
  ```

##### `list_resources(type_filter: Optional[ResourceType] = None) -> List[Resource]`

- **Description**: List resources, optionally filtered by type.

##### `add_resource(resource: Resource) -> bool`

- **Description**: Add (or replace) a resource.

---

## Data Models

### WorkflowExecution Class

`WorkflowManager.execute_workflow` returns a finished `WorkflowExecution`:

```python
@dataclass
class WorkflowExecution:
    workflow_name: str
    execution_id: str
    start_time: datetime
    status: WorkflowStatus = WorkflowStatus.PENDING  # COMPLETED or FAILED once returned
    step_results: Dict[str, Any] = field(default_factory=dict)  # step name -> TaskResult.to_dict()
    end_time: Optional[datetime] = None  # set when execution finishes
    error: Optional[str] = None  # "<step>: <error>; ..." for failed required steps

    duration: Optional[float]  # property, seconds
    success: bool  # property, status == COMPLETED
```

### WorkflowStep Class

```python
@dataclass
class WorkflowStep:
    name: str  # Unique identifier for this step within the workflow
    module: str  # Module path relative to codomyrmex (e.g. 'coding.static_analysis') or a registered module name
    action: str  # Callable to invoke within the module
    parameters: Dict[str, Any] = field(default_factory=dict)  # Keyword arguments for the action
    run_if: Optional[str] = None  # Not supported: execution raises NotImplementedError if set
    dependencies: List[str] = field(default_factory=list)  # Step names that must complete first
    required: bool = True  # A failed non-required step does not fail the workflow
    timeout: Optional[float] = None  # Recorded on the task; not enforced
    retry_count: int = 0  # Recorded on the task; retries are not performed
```

### Task Class

```python
@dataclass
class Task:
    name: str
    module: str  # See "Task Dispatch"
    action: str
    parameters: Dict[str, Any] = field(default_factory=dict)  # Keyword arguments for the action
    priority: TaskPriority = TaskPriority.NORMAL
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    dependencies: List[str] = field(default_factory=list)  # Task IDs this depends on
    resources: List[TaskResource] = field(default_factory=list)  # Allocated around execution
    timeout: Optional[float] = None  # Recorded; not enforced
    retry_count: int = 0  # Recorded; retries are not performed
    max_retries: int = 3  # Recorded; retries are not performed
    metadata: Dict[str, Any] = field(default_factory=dict)

    # Runtime state
    status: TaskStatus = TaskStatus.PENDING
    result: Optional[TaskResult] = None
    error: Optional[str] = None
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    allocations: List[ResourceAllocation] = field(default_factory=list)  # held while running
```

### Project Class

```python
@dataclass
class Project:
    name: str
    path: Path
    type: ProjectType
    description: str = ""
    status: ProjectStatus = ProjectStatus.PLANNING
    config: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime
    updated_at: datetime
    owner: Optional[str] = None
    version: str = "0.1.0"
    metrics: Dict[str, Any] = field(default_factory=dict)
    milestones: Dict[str, Dict[str, Any]] = field(default_factory=dict)

    metadata_file: Path  # property: path / "project.json" (PROJECT_FILE_NAME)
    def to_dict(self) -> Dict[str, Any]: ...  # JSON-ready: str path, enum values, ISO 8601 datetimes
    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "Project": ...
```

`Project.from_dict` restores `to_dict` output: `name`, `path`, `type`, `status`, `created_at` and `updated_at` are required, the rest default. It raises `ValueError` for a missing field, a wrong type, an unknown enum value or a timestamp without a UTC offset.

### Resource Class

```python
@dataclass
class Resource:
    id: str  # Unique resource identifier
    name: str  # Human-readable resource name
    type: ResourceType
    capacity: float = 1.0
    description: str = ""
    limits: ResourceLimits = field(default_factory=ResourceLimits)
    status: ResourceStatus = ResourceStatus.AVAILABLE
    metadata: Dict[str, Any] = field(default_factory=dict)
    allocated: float = 0.0  # Currently allocated amount
    allocations: Dict[str, ResourceAllocation] = field(default_factory=dict)
```

The default `ResourceManager` registers `sys-compute` (compute, capacity 100), `sys-memory` (memory, 1024) and `api-global` (api_quota, 1000).

### TaskResource Class

```python
@dataclass
class TaskResource:
    resource_type: str  # A ResourceType value, e.g. "memory"
    amount: float = 1.0
    resource_id: Optional[str] = None  # Use this specific resource
```

### ResourceAllocation Class

```python
@dataclass
class ResourceAllocation:
    allocation_id: str
    resource_id: str
    requester_id: str  # Task ID or user ID
    amount: float
    timestamp: datetime
    expires_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
```

## Enumerations

### WorkflowStatus

- `PENDING`: Workflow is pending execution
- `RUNNING`: Workflow is currently executing
- `COMPLETED`: Workflow completed successfully
- `FAILED`: Workflow execution failed
- `CANCELLED`: Workflow was cancelled

### TaskStatus

- `PENDING`: Task was submitted
- `READY`: Task is queued (dependencies satisfied)
- `BLOCKED`: Task is waiting for dependencies
- `RUNNING`: Task is currently executing
- `COMPLETED`: Task completed successfully
- `FAILED`: Task failed, could not be dispatched, or a dependency failed
- `CANCELLED`: Task was cancelled

### TaskPriority

- `CRITICAL` (0), `HIGH` (1), `NORMAL` (2), `LOW` (3), `BACKGROUND` (4); lower values run first

### ProjectStatus

- `PLANNING`: Project is in planning phase
- `ACTIVE`: Project is actively being worked on
- `PAUSED`: Project work is paused
- `COMPLETED`: Project is completed
- `ARCHIVED`: Project is archived
- `FAILED`: Project failed

### ResourceType

Values: `compute`, `memory`, `storage`, `network`, `api_quota`, `database`, `custom`, `file_handle`, `thread`, `process`, `lock`.

### ResourceStatus

Values: `available`, `allocated`, `busy` (fully allocated), `maintenance`, `offline`, `depleted`, `unknown`. Tasks wait for `available`/`allocated`/`busy` resources and fail on the others.

### OrchestrationMode

- `SEQUENTIAL`: Execute workflows/tasks one after another
- `PARALLEL`: Execute workflows/tasks in parallel when possible
- `PRIORITY`: Execute based on priority ordering
- `RESOURCE_AWARE`: Execute based on resource availability

### SessionStatus

- `PENDING`: Session is pending
- `ACTIVE`: Session is active
- `COMPLETED`: Session completed successfully
- `CANCELLED`: Session was cancelled
- `FAILED`: Session failed

## Error Handling

### Exception Classes

#### `OrchestrationError`

Base exception for orchestration operations.

#### `WorkflowExecutionError`

Raised when workflow execution fails.

#### `TaskExecutionError`

`codomyrmex.exceptions.TaskExecutionError`. Raised when a task's `module`/`action` cannot be resolved or a resource requirement can never be met; the orchestrator records its message as the task's `error`. Also raised by `TaskOrchestrator.wait_for_tasks` when processing was stopped while tasks are still queued.

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
from codomyrmex.logistics.orchestration.project import WorkflowStep, get_orchestration_engine

engine = get_orchestration_engine()
engine.workflow_manager.create_workflow(
    "quality",
    [WorkflowStep(name="analyze", module="coding.static_analysis",
                  action="analyze_project", parameters={"project_root": "./src"})],
)
result = engine.execute_workflow("quality")

if result["success"]:
    print(f"Analysis completed in {result['execution_time']} seconds")
    print(f"Results: {result['result']['analyze']['result']}")
else:
    print(f"Analysis failed: {result['error']}")
```

### Project-based Development

```python
from codomyrmex.logistics.orchestration.project import ProjectType, get_orchestration_engine

engine = get_orchestration_engine()

# Create project
project = engine.project_manager.create_project(
    "chatbot-analysis",
    ProjectType.AI_ANALYSIS,
    description="AI analysis of chatbot conversations",
)

# Execute a registered workflow for the project (recorded in project.metrics)
result = engine.execute_project_workflow("chatbot-analysis", "quality")

# Track milestone
engine.project_manager.add_project_milestone(
    "chatbot-analysis",
    "initial_analysis_complete",
    {"success": result["success"]},
)
```

### Custom Task Orchestration

```python
from codomyrmex.logistics.orchestration.project import (
    Task,
    TaskPriority,
    TaskResource,
    TaskOrchestrator,
)

orchestrator = TaskOrchestrator(max_workers=4)
orchestrator.register_action("reports", "render", lambda findings: f"{len(findings)} findings")

analysis_task = Task(
    name="analyze_code",
    module="coding.static_analysis",
    action="analyze_project",
    parameters={"project_root": "./src"},
    priority=TaskPriority.HIGH,
    resources=[TaskResource(resource_type="compute", amount=2)],
)
report_task = Task(
    name="render_report",
    module="reports",
    action="render",
    parameters={"findings": []},
    dependencies=[analysis_task.id],
)
orchestrator.submit_task(analysis_task)
orchestrator.submit_task(report_task)

if orchestrator.wait_for_tasks([analysis_task.id, report_task.id], timeout=300):
    for task in (analysis_task, report_task):
        result = orchestrator.get_task_result(task.id)
        print(task.name, result.status.value, result.result or result.error)
else:
    print("Task execution timed out")
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

## Navigation Links

- **Parent**: [Project Overview](../README.md)
- **Module Index**: [All Agents](../../AGENTS.md)
- **Documentation**: [Reference Guides](../../../../../docs/README.md)
- **Home**: [Root README](../../../README.md)
