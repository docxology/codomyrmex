# Orchestrator Module API Specification

**Version**: v1.1.9 | **Status**: Stable | **Last Updated**: February 2026

## 1. Overview

The `orchestrator` module provides a flexible workflow execution layer for discovering, configuring, and running Python scripts and functions. It supports DAG-based task dependencies, parallel execution, retry logic with exponential backoff, async scheduling, and integration bridges for CI/CD and agent orchestration.

## 2. Core Components

### 2.1 Top-Level Entry Points

```python
from codomyrmex.orchestrator import run_orchestrator, load_config, get_script_config, discover_scripts

def run_orchestrator(argv: list[str] | None = None) -> int:
    """Parse arguments, discover and run scripts, report results; returns the exit code."""

def load_config(scripts_dir: Path) -> dict[str, Any]:
    """Load config.yaml/config.yml (or scripts_config.json), searching upwards from scripts_dir."""

def get_script_config(script_path: Path, scripts_dir: Path, global_config: dict[str, Any]) -> dict[str, Any]:
    """Resolve one script's settings: defaults, skip list, timeout overrides and per-script entries."""

def discover_scripts(
    scripts_dir: Path,
    subdirs: list[str] | None = None,
    pattern: str | None = None,
    max_depth: int = 2,
) -> list[Path]:
    """Discover Python scripts under scripts_dir, optionally filtered by subdirectory and glob pattern."""
```

### 2.2 Workflow DAG

The core workflow model uses a DAG of `Task` objects executed by a `Workflow` engine.

```python
from codomyrmex.orchestrator import Workflow, Task, TaskStatus, TaskResult, RetryPolicy

class TaskStatus(Enum):
    PENDING   = "pending"
    RUNNING   = "running"
    COMPLETED = "completed"
    FAILED    = "failed"
    SKIPPED   = "skipped"
    RETRYING  = "retrying"

@dataclass
class RetryPolicy:
    max_attempts: int = 3
    initial_delay: float = 1.0       # seconds
    max_delay: float = 60.0          # seconds
    exponential_base: float = 2.0
    retry_on: tuple = (Exception,)   # exception types to retry

    def get_delay(self, attempt: int) -> float:
        """Calculate backoff delay for attempt N."""

@dataclass
class TaskResult:
    success: bool
    value: Any = None
    error: str | None = None
    execution_time: float = 0.0
    attempts: int = 1

@dataclass
class Task:
    name: str
    action: Callable[..., Any]
    args: list[Any] = field(default_factory=list)
    kwargs: dict[str, Any] = field(default_factory=dict)
    dependencies: set[str] = field(default_factory=set)
    timeout: float | None = None
    retry_policy: RetryPolicy | None = None
    condition: Callable[[dict[str, TaskResult]], bool] | None = None

class Workflow:
    """DAG-based workflow executor."""
    def __init__(
        self,
        name: str,
        timeout: float | None = None,
        fail_fast: bool = True,
        progress_callback: Callable[[str, str, dict[str, Any]], None] | None = None,
        event_bus: Any = None,
    ): ...
    def add_task(self, name: str, action: Callable[..., Any], **opts: Any) -> "Workflow":
        """Add a task; returns self. Options: dependencies, args, kwargs, timeout,
        retry_policy, condition, transform_result, tags, metadata."""
    def validate(self) -> None: ...
    async def run(self) -> dict[str, Any]: ...
    def get_task_result(self, task_name: str) -> TaskResult | None: ...
    def get_summary(self) -> dict[str, Any]: ...
    def cancel(self) -> None: ...
```

> **Note on `orchestrator.pipelines`**: The `pipelines` submodule provides a separate `Pipeline` class
> with a **synchronous** `run()` method (not `async def execute()`). See section 2.2.1 below.

### 2.2.1 Pipeline (synchronous)

The `orchestrator.pipelines` module provides a `Pipeline` class with synchronous execution:

```python
from codomyrmex.orchestrator.pipelines import Pipeline, FunctionStage, PipelineBuilder

class Pipeline:
    """Pipeline for orchestrating multi-stage workflows."""
    def __init__(self, pipeline_id: str | None = None, name: str | None = None, fail_fast: bool = True): ...
    def add_stage(self, stage: Stage) -> "Pipeline": ...
    def set_context(self, key: str, value: Any) -> "Pipeline": ...
    def run(self, initial_context: dict[str, Any] | None = None) -> PipelineResult: ...
```

The `run()` method is synchronous. It resolves stage execution order via topological sort,
executes stages sequentially (respecting `depends_on` declarations), and returns a `PipelineResult`.

### 2.3 Workflow Helper Functions

```python
from codomyrmex.orchestrator import chain, parallel, fan_out_fan_in

def chain(*actions: Callable, names: list[str] | None = None) -> Workflow:
    """Create a workflow where each action depends on the previous one."""

def parallel(*actions: Callable, names: list[str] | None = None) -> Workflow:
    """Create a workflow where all actions run concurrently (no dependencies)."""

def fan_out_fan_in(
    initial: Callable,
    parallel_tasks: list[Callable],
    final: Callable,
    initial_name: str = "initial",
    final_name: str = "final",
) -> Workflow:
    """Run initial, then parallel_tasks concurrently, then final."""
```

### 2.4 Exceptions

```python
from codomyrmex.orchestrator import (
    WorkflowError,
    CycleError,
    TaskFailedError,
    StepError,
    OrchestratorTimeoutError,
    StateError,
    DependencyResolutionError,
    ConcurrencyError,
)

class WorkflowError(Exception): ...         # Base workflow exception
class CycleError(WorkflowError): ...        # Cycle detected in task DAG
class TaskFailedError(WorkflowError): ...   # Task exceeded retries or hard-failed
class StepError(Exception): ...             # Error in a thin-orchestration step
class OrchestratorTimeoutError(Exception): ...  # Workflow-wide timeout exceeded
class StateError(Exception): ...            # Invalid state transition
class DependencyResolutionError(Exception): ...  # Unresolvable task dependency
class ConcurrencyError(Exception): ...      # Resource contention in parallel execution
```

## 3. Script Runners

### 3.1 Synchronous Runners

```python
from codomyrmex.orchestrator import run_script, run_function, ParallelRunner, BatchRunner, ExecutionResult

@dataclass
class ExecutionResult:
    """Result of a parallel batch of scripts."""
    total: int = 0
    passed: int = 0
    failed: int = 0
    timeout: int = 0
    skipped: int = 0
    execution_time: float = 0.0
    results: list[dict[str, Any]] = field(default_factory=list)  # one run_script() dict per script
    # property: success -> bool (no failures or timeouts); to_dict()

def run_script(
    script_path: Path,
    timeout: int = 60,
    env: dict[str, str] | None = None,
    cwd: Path | None = None,
    config: dict[str, Any] | None = None,
    memory_limit_mb: int | None = None,
) -> dict[str, Any]:
    """Run a Python script in a subprocess. The result dict has script, name, status,
    exit_code, stdout, stderr, error, start_time, end_time and execution_time.
    config may set timeout, args, env and allowed_exit_codes."""

def run_function(
    func: Callable,
    args: tuple = (),
    kwargs: dict | None = None,
    timeout: int = 60,
    memory_limit_mb: int | None = None,
) -> dict[str, Any]:
    """Run a Python callable in a monitored separate process and return a result dict."""

class ParallelRunner:
    """Run scripts concurrently using a thread pool."""
    def __init__(
        self,
        max_workers: int | None = None,
        progress_callback: Callable[[str, str, dict[str, Any]], None] | None = None,
        default_timeout: int = 60,
        fail_fast: bool = False,
    ): ...
    def run_scripts(
        self,
        scripts: list[Path],
        timeout: int | None = None,
        cwd: Path | None = None,
        env: dict[str, str] | None = None,
        configs: dict[str, dict[str, Any]] | None = None,
        context: ExecutionContext | None = None,
    ) -> ExecutionResult: ...
    async def run_scripts_async(self, scripts: list[Path], timeout: int | None = None, cwd: Path | None = None, env: dict[str, str] | None = None, configs: dict[str, dict[str, Any]] | None = None) -> ExecutionResult: ...

class BatchRunner:
    """Run batches of scripts one after another, each batch in parallel."""
    def __init__(self, max_workers: int | None = None, progress_callback: Callable[[str, str, dict[str, Any]], None] | None = None): ...
    def run_batches(
        self,
        batches: list[list[Path]],
        timeout: int = 60,
        cwd: Path | None = None,
        stop_on_batch_failure: bool = True,
    ) -> list[ExecutionResult]: ...

def run_parallel(
    scripts: list[Path],
    max_workers: int | None = None,
    timeout: int = 60,
    progress_callback: Callable[[str, str, dict[str, Any]], None] | None = None,
) -> ExecutionResult:
    """Run scripts in parallel and return the aggregated result."""

async def run_parallel_async(
    scripts: list[Path],
    max_workers: int | None = None,
    timeout: int = 60,
    progress_callback: Callable[[str, str, dict[str, Any]], None] | None = None,
) -> ExecutionResult:
    """Async variant of run_parallel."""
```

### 3.2 Async Runners

```python
from codomyrmex.orchestrator import (
    AsyncParallelRunner, AsyncTaskResult, AsyncExecutionResult,
    AsyncScheduler, AsyncJob, AsyncJobStatus, SchedulerMetrics,
)

@dataclass
class AsyncTaskResult:
    name: str
    success: bool
    value: Any = None
    error: str | None = None
    error_type: str | None = None
    execution_time: float = 0.0

@dataclass
class AsyncExecutionResult:
    batch_id: str
    total: int
    passed: int
    failed: int
    cancelled: int
    execution_time: float
    results: list[AsyncTaskResult]

class AsyncParallelRunner:
    """Async parallel task executor using asyncio."""
    def __init__(self, *, max_concurrency: int | None = None, fail_fast: bool = False, on_task_complete: OnTaskComplete | None = None): ...
    async def run(self, tasks: list[tuple[str, Callable[..., Coroutine[Any, Any, Any]], tuple[Any, ...]]]) -> AsyncExecutionResult: ...

class AsyncJobStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

@dataclass
class AsyncJob:
    id: str
    name: str
    func: Callable[..., Coroutine[Any, Any, Any]] | None
    args: tuple[Any, ...]
    kwargs: dict[str, Any]
    priority: int
    status: AsyncJobStatus
    result: Any
    error: str | None
    scheduled_at: datetime
    started_at: datetime | None
    completed_at: datetime | None
    max_runs: int | None

@dataclass
class SchedulerMetrics:
    jobs_scheduled: int
    jobs_completed: int
    jobs_failed: int
    jobs_cancelled: int
    total_execution_time: float

class AsyncScheduler:
    """Async job scheduler with metrics."""
    def __init__(self, *, max_concurrency: int = 4, event_bus: Any = None): ...
    def schedule(
        self,
        func: Callable[..., Coroutine[Any, Any, Any]],
        *,
        name: str | None = None,
        args: tuple[Any, ...] = (),
        kwargs: dict[str, Any] | None = None,
        priority: int = 0,
        max_runs: int | None = 1,
    ) -> str: ...  # returns the job id
    def cancel(self, job_id: str) -> bool: ...
    def get_job(self, job_id: str) -> AsyncJob | None: ...
    def list_jobs(self, status: AsyncJobStatus | None = None) -> list[AsyncJob]: ...
    async def run_all(self) -> dict[str, AsyncJob]: ...
    # property: metrics -> SchedulerMetrics
```

## 4. Retry Decorator

```python
from codomyrmex.orchestrator import with_retry

def with_retry(
    *,
    max_attempts: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential_base: float = 2.0,
    retry_on: tuple[type[Exception], ...] = (Exception,),
) -> Callable[[F], F]:
    """Decorator: retry a sync or async callable with exponential backoff."""

# Usage:
@with_retry(max_attempts=5, base_delay=0.5)
def flaky_network_call():
    ...
```

## 5. Thin Orchestration Utilities

High-level, one-liner helpers for rapid workflow construction.

```python
from codomyrmex.orchestrator import (
    run, run_async, pipe, batch, chain_scripts,
    workflow, step, Steps, StepResult,
    shell, python_func, retry, timeout, condition,
)

def run(
    target: str | Path,
    timeout: int = 60,
    args: list[str] | None = None,
    env: dict[str, str] | None = None,
    cwd: Path | None = None,
) -> dict[str, Any]:
    """Run a single script or shell command and return a result dict."""

async def run_async(target: str | Path, timeout: int = 60, args: list[str] | None = None) -> dict[str, Any]: ...

def pipe(commands: list[str], timeout_per_command: int = 30, stop_on_error: bool = True) -> dict[str, Any]:
    """Run shell commands in order; each gets the previous stdout in $PIPE_INPUT."""

def batch(targets: list[str | Path], workers: int | None = None, timeout: int = 60) -> ExecutionResult:
    """Run multiple scripts or commands in parallel and aggregate the results."""

def chain_scripts(
    scripts: list[str | Path],
    timeout_per_script: int = 60,
    pass_results: bool = True,
    stop_on_error: bool = True,
) -> dict[str, Any]:
    """Run scripts sequentially, optionally passing results via the environment."""

# Workflow builder DSL
def workflow(name: str = "workflow") -> Steps: ...  # builder: add(), add_parallel(), run(), run_sync()
def step(name: str, action: Callable | None = None, timeout: float | None = None, retry: int = 1): ...  # decorator
def shell(command: str, timeout: int = 60, env: dict[str, str] | None = None, cwd: Any = None, check: bool = False) -> dict[str, Any]: ...
def python_func(func: Callable, args: tuple = (), kwargs: dict | None = None, timeout: int = 60) -> dict[str, Any]: ...
def retry(action: Callable, max_attempts: int = 3, delay: float = 1.0, backoff: float = 2.0) -> Callable: ...
def timeout(seconds: float) -> Callable: ...  # decorator
def condition(predicate: Callable[[dict], bool]) -> Callable: ...

@dataclass
class StepResult:
    success: bool
    value: Any = None
    error: str | None = None
    execution_time: float = 0.0
```

## 6. Integration Bridges

```python
from codomyrmex.orchestrator import (
    OrchestratorBridge, CICDBridge, AgentOrchestrator,
    StageConfig, PipelineConfig,
    create_pipeline_workflow, run_ci_stage, run_agent_task,
)

@dataclass
class StageConfig:
    name: str
    commands: list[str]
    parallel: bool = True
    allow_failure: bool = False
    timeout: int = 300
    retry: int = 0
    environment: dict[str, str] = field(default_factory=dict)
    condition: Callable[[dict], bool] | None = None

@dataclass
class PipelineConfig:
    name: str
    stages: list[StageConfig]
    variables: dict[str, str] = field(default_factory=dict)
    timeout: int = 3600
    fail_fast: bool = True

class OrchestratorBridge:
    """Bridge between the orchestrator and an external execution engine."""
    def __init__(self, engine=None): ...
    def create_session(self, **kwargs) -> str | None: ...
    def close_session(self) -> bool: ...
    def execute_workflow(self, workflow_name: str, **params) -> dict[str, Any]: ...
    def run_quick(self, target: str | Path, timeout: int = 60, **kwargs) -> dict[str, Any]: ...
    def create_workflow(self, name: str = "workflow") -> Steps: ...

class CICDBridge:
    """CI/CD pipeline integration."""
    def __init__(self, workspace_dir: str | None = None): ...
    def create_workflow_from_pipeline(self, pipeline_config: PipelineConfig | dict[str, Any]) -> Workflow: ...
    async def run_stage(self, stage_config: StageConfig, env: dict[str, str] | None = None) -> dict[str, Any]: ...

class AgentOrchestrator:
    """Run agent tasks within the orchestrator DAG."""
    def __init__(self, capability_profile: dict[str, list[str]] | None = None): ...
    async def run_agent_task(self, agent_name: str, task: str, **kwargs) -> dict[str, Any]: ...

def create_pipeline_workflow(stages: list[dict[str, Any]], name: str = "pipeline", fail_fast: bool = True) -> Workflow:
    """Build a Workflow from stage configuration mappings."""

async def run_ci_stage(
    name: str,
    commands: list[str],
    timeout: int = 300,
    env: dict[str, str] | None = None,
    allow_failure: bool = False,
) -> dict[str, Any]:
    """Run one CI/CD stage's commands and return the stage result."""

async def run_agent_task(agent_name: str, task: str, orchestrator: AgentOrchestrator | None = None, **kwargs) -> dict[str, Any]:
    """Run a task with a registered agent."""
```

## 7. MCP Tools

```python
from codomyrmex.orchestrator.mcp_tools import get_scheduler_metrics, analyze_workflow_dependencies

def get_scheduler_metrics() -> SchedulerMetrics:
    """Return current scheduler state: active jobs, queue depth, throughput."""

def analyze_workflow_dependencies(tasks: list[dict]) -> dict:
    """
    Validate a task list for DAG validity and return execution order.

    Input:  [{"id": "build", "depends_on": []}, {"id": "test", "depends_on": ["build"]}, ...]
    Output: {"execution_order": [...], "parallel_groups": [[...], [...]]}
    Raises: CycleError if circular dependencies detected.
    """
```

## 8. CLI Integration

```python
from codomyrmex.orchestrator import cli_commands

commands = cli_commands()
# commands["workflows"]["handler"]()  → print available workflows
# commands["run"]["handler"](name="ci")  → run named workflow
```

## 9. Usage Examples

```python
# Build a DAG and run it
import asyncio

from codomyrmex.orchestrator import Workflow

wf = Workflow("report")
wf.add_task("fetch", fetch_data, args=["https://api.example.com"])
wf.add_task("validate", validate_config, dependencies=["fetch"])
wf.add_task("report", generate_report, dependencies=["validate"])
results = asyncio.run(wf.run())
# ...or build via the chain / parallel / fan_out_fan_in helpers
```

```python
# Retry decorator
from codomyrmex.orchestrator import with_retry

@with_retry(max_attempts=3, base_delay=2.0, retry_on=(ConnectionError,))
def call_external_api():
    ...
```

```python
# Thin orchestration one-liner
from codomyrmex.orchestrator import pipe

result = pipe(["echo hello", "echo world"])
print(result["success"], result["final_output"])
```

## 10. Error Handling

| Exception | When raised |
| --- | --- |
| `CycleError` | Task DAG has a circular dependency |
| `TaskFailedError` | Task exhausted all retry attempts |
| `OrchestratorTimeoutError` | Workflow-wide deadline exceeded |
| `DependencyResolutionError` | A task depends on an undeclared task name |
| `ConcurrencyError` | Thread/process pool resource contention |
| `StateError` | Invalid workflow state transition attempted |

## 11. Configuration

No required environment variables for core orchestration. Optional integrations:

| Variable | Module | Purpose |
| --- | --- | --- |
| `CODOMYRMEX_MAX_WORKERS` | `parallel_runner` | Default thread pool size (default: 4) |
| `CODOMYRMEX_SCRIPT_ROOT` | `discovery` | Root directory for script discovery |
| `CODOMYRMEX_WORKFLOW_TIMEOUT` | `workflow` | Global workflow deadline in seconds |
