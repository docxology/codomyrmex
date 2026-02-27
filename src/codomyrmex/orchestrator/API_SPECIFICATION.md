# Orchestrator Module API Specification

**Version**: v0.1.7 | **Status**: Stable | **Last Updated**: February 2026

## 1. Overview

The `orchestrator` module provides a flexible workflow execution layer for discovering, configuring, and running Python scripts and functions. It supports DAG-based task dependencies, parallel execution, retry logic with exponential backoff, async scheduling, and integration bridges for CI/CD and agent orchestration.

## 2. Core Components

### 2.1 Top-Level Entry Points

```python
from codomyrmex.orchestrator import run_orchestrator, load_config, get_script_config, discover_scripts

def run_orchestrator() -> None:
    """Launch the interactive orchestrator CLI menu."""

def load_config(path: str | None = None) -> dict:
    """Load orchestrator configuration from file or defaults."""

def get_script_config(script_name: str) -> dict:
    """Retrieve configuration metadata for a named script."""

def discover_scripts(root: str | None = None) -> list[str]:
    """Discover all runnable scripts in the project tree."""
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
    def add_task(self, task: Task) -> None: ...
    async def execute(
        self,
        progress_callback: Callable[[str, TaskStatus, TaskResult | None], None] | None = None,
    ) -> dict[str, TaskResult]: ...
```

### 2.3 Workflow Helper Functions

```python
from codomyrmex.orchestrator import chain, parallel, fan_out_fan_in

def chain(*tasks: Task) -> Workflow:
    """Create a workflow where each task depends on the previous one."""

def parallel(*tasks: Task) -> Workflow:
    """Create a workflow where all tasks run concurrently (no dependencies)."""

def fan_out_fan_in(fan_out: list[Task], fan_in: Task) -> Workflow:
    """Fan out to N parallel tasks then converge to a single aggregator task."""
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
    success: bool
    output: str
    error: str
    return_code: int
    execution_time: float

def run_script(script_path: str, args: list[str] | None = None) -> ExecutionResult:
    """Execute a Python script as a subprocess."""

def run_function(func: Callable, *args, **kwargs) -> ExecutionResult:
    """Execute a Python callable, capturing output and timing."""

class ParallelRunner:
    """Execute multiple callables concurrently using a thread pool."""
    def __init__(self, max_workers: int = 4): ...
    def run(self, tasks: list[Callable]) -> list[ExecutionResult]: ...

class BatchRunner:
    """Execute scripts in configurable batches."""
    def run_batch(self, scripts: list[str], batch_size: int = 4) -> list[ExecutionResult]: ...

def run_parallel(tasks: list[Callable], max_workers: int = 4) -> list[ExecutionResult]:
    """Convenience function: run tasks in parallel and return all results."""

async def run_parallel_async(tasks: list[Callable], max_workers: int = 4) -> list[ExecutionResult]:
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
    task_id: str
    success: bool
    value: Any
    error: str | None
    execution_time: float

@dataclass
class AsyncExecutionResult:
    results: list[AsyncTaskResult]
    total_time: float
    success_count: int
    failure_count: int

class AsyncParallelRunner:
    """Async parallel task executor using asyncio."""
    async def run(self, tasks: list[Callable]) -> AsyncExecutionResult: ...

class AsyncJobStatus(Enum):
    QUEUED = "queued"
    RUNNING = "running"
    DONE = "done"
    FAILED = "failed"

@dataclass
class AsyncJob:
    job_id: str
    func: Callable
    status: AsyncJobStatus
    result: Any | None = None

@dataclass
class SchedulerMetrics:
    active_jobs: int
    queued_jobs: int
    completed_jobs: int
    failed_jobs: int
    throughput_per_second: float

class AsyncScheduler:
    """Persistent async job scheduler with metrics."""
    async def submit(self, func: Callable, *args, **kwargs) -> AsyncJob: ...
    async def get_metrics(self) -> SchedulerMetrics: ...
    async def cancel(self, job_id: str) -> bool: ...
```

## 4. Retry Decorator

```python
from codomyrmex.orchestrator import with_retry

def with_retry(
    max_attempts: int = 3,
    initial_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential_base: float = 2.0,
    retry_on: tuple = (Exception,),
) -> Callable:
    """Decorator: wrap any callable with automatic retry-with-backoff logic."""

# Usage:
@with_retry(max_attempts=5, initial_delay=0.5)
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

def run(script: str, args: list[str] | None = None) -> ExecutionResult:
    """Run a single script — one-liner convenience wrapper."""

async def run_async(script: str) -> ExecutionResult: ...

def pipe(commands: list[str]) -> ExecutionResult:
    """Pipe shell commands sequentially, feeding stdout of each to the next."""

def batch(scripts: list[str], max_workers: int = 4) -> list[ExecutionResult]:
    """Run multiple scripts in parallel, collect results."""

def chain_scripts(*scripts: str) -> list[ExecutionResult]:
    """Run scripts sequentially, stopping on first failure."""

# Workflow builder DSL
def workflow(*steps: 'Steps') -> Workflow: ...
def step(name: str, action: Callable, **kwargs) -> 'Steps': ...
def shell(command: str) -> Callable: ...
def python_func(func: Callable) -> Callable: ...
def retry(action: Callable, attempts: int = 3) -> Callable: ...
def timeout(action: Callable, seconds: float) -> Callable: ...
def condition(predicate: Callable[..., bool], action: Callable) -> Callable: ...

@dataclass
class StepResult:
    name: str
    success: bool
    output: Any
    error: str | None
    duration: float
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
    env: dict[str, str] = field(default_factory=dict)
    timeout: float | None = None
    retry_on_failure: bool = False

@dataclass
class PipelineConfig:
    stages: list[StageConfig]
    parallel_stages: list[list[str]] = field(default_factory=list)

class OrchestratorBridge:
    """Generic bridge for connecting orchestrator to external systems."""
    def run_pipeline(self, config: PipelineConfig) -> list[ExecutionResult]: ...

class CICDBridge(OrchestratorBridge):
    """CI/CD system integration (GitHub Actions, Jenkins, etc.)."""
    def run_ci_stage(self, stage: StageConfig) -> ExecutionResult: ...

class AgentOrchestrator:
    """Run agent tasks within the orchestrator DAG."""
    async def run_agent_task(self, agent_name: str, task: str) -> TaskResult: ...

def create_pipeline_workflow(config: PipelineConfig) -> Workflow:
    """Convert a PipelineConfig into a fully-wired Workflow DAG."""

def run_ci_stage(stage: StageConfig) -> ExecutionResult:
    """Module-level convenience wrapper for CICDBridge.run_ci_stage."""

def run_agent_task(agent_name: str, task: str) -> TaskResult:
    """Module-level convenience wrapper for AgentOrchestrator.run_agent_task."""
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
# Simple parallel execution
from codomyrmex.orchestrator import parallel, Task

tasks = [
    Task("fetch", action=fetch_data, args=["https://api.example.com"]),
    Task("validate", action=validate_config, dependencies={"fetch"}),
    Task("report", action=generate_report, dependencies={"validate"}),
]
wf = parallel(tasks[0])   # fetch runs first
# ...or build via chain/fan_out_fan_in helpers
```

```python
# Retry decorator
from codomyrmex.orchestrator import with_retry

@with_retry(max_attempts=3, initial_delay=2.0, retry_on=(ConnectionError,))
def call_external_api():
    ...
```

```python
# Thin orchestration one-liner
from codomyrmex.orchestrator import pipe

result = pipe(["echo hello", "tr '[:lower:]' '[:upper:]'"])
print(result.output)  # "HELLO\n"
```

## 10. Error Handling

| Exception | When raised |
|-----------|------------|
| `CycleError` | Task DAG has a circular dependency |
| `TaskFailedError` | Task exhausted all retry attempts |
| `OrchestratorTimeoutError` | Workflow-wide deadline exceeded |
| `DependencyResolutionError` | A task depends on an undeclared task name |
| `ConcurrencyError` | Thread/process pool resource contention |
| `StateError` | Invalid workflow state transition attempted |

## 11. Configuration

No required environment variables for core orchestration. Optional integrations:

| Variable | Module | Purpose |
|----------|--------|---------|
| `CODOMYRMEX_MAX_WORKERS` | `parallel_runner` | Default thread pool size (default: 4) |
| `CODOMYRMEX_SCRIPT_ROOT` | `discovery` | Root directory for script discovery |
| `CODOMYRMEX_WORKFLOW_TIMEOUT` | `workflow` | Global workflow deadline in seconds |
