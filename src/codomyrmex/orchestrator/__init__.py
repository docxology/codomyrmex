"""
Script Orchestrator Module

This module provides functionality for discovering, configuring, and running
Python scripts within the Codomyrmex project.

Features:
- Script discovery and execution
- Workflow DAG execution with dependencies
- Parallel execution with resource management
- Retry logic and conditional execution
- Progress streaming and callbacks


Submodules:
    scheduler: Consolidated scheduler capabilities."""

# Shared schemas for cross-module interop
try:
    from codomyrmex.validation.schemas import Result, ResultStatus
except ImportError:
    Result = None
    ResultStatus = None

# New submodule exports
from . import (
    engines,
    execution,
    monitors,
    observability,
    pipelines,
    resilience,
    scheduler,
    state,
    templates,
    triggers,
    workflows,
)
from .config import get_script_config, load_config
from .core import main as run_orchestrator
from .discovery import discover_scripts
from .exceptions import (
    ConcurrencyError,
    DependencyResolutionError,
    OrchestratorTimeoutError,
    StateError,
    StepError,
)
from .execution.async_runner import (
    AsyncExecutionResult,
    AsyncParallelRunner,
    AsyncTaskResult,
)
from .execution.async_scheduler import (
    AsyncJob,
    AsyncJobStatus,
    AsyncScheduler,
    SchedulerMetrics,
)
from .execution.parallel_runner import (
    BatchRunner,
    ExecutionResult,
    ParallelRunner,
    run_parallel,
    run_parallel_async,
)
from .execution.runner import run_function, run_script
from .integration import (
    AgentOrchestrator,
    CICDBridge,
    OrchestratorBridge,
    PipelineConfig,
    StageConfig,
    create_pipeline_workflow,
    run_agent_task,
    run_ci_stage,
)
from .resilience.retry_policy import with_retry
from .thin import (
    StepResult,
    Steps,
    batch,
    chain_scripts,
    condition,
    pipe,
    python_func,
    retry,
    run,
    run_async,
    shell,
    step,
    timeout,
    workflow,
)
from .workflows.workflow import (
    CycleError,
    RetryPolicy,
    Task,
    TaskFailedError,
    TaskResult,
    TaskStatus,
    Workflow,
    WorkflowError,
    chain,
    fan_out_fan_in,
    parallel,
)


def cli_commands():
    """Return CLI commands for the orchestrator module."""
    return {
        "workflows": {
            "help": "List available workflows",
            "handler": lambda **kwargs: print(
                "Available workflows:\n"
                + "\n".join(f"  - {name}" for name in ["default", "ci", "deploy", "test"])
            ),
        },
        "run": {
            "help": "Run a workflow by name",
            "args": {"--name": {"help": "Workflow name to run", "required": True}},
            "handler": lambda name="default", **kwargs: print(
                f"Running workflow: {name}"
            ),
        },
    }


__all__ = [
    "scheduler",
    # CLI integration
    "cli_commands",
    'templates',
    'state',
    'triggers',
    'pipelines',
    # Core orchestration
    "run_orchestrator",
    "load_config",
    "get_script_config",
    "discover_scripts",
    # Workflow
    "Workflow",
    "Task",
    "TaskStatus",
    "TaskResult",
    "RetryPolicy",
    "WorkflowError",
    "CycleError",
    "TaskFailedError",
    # Additional exceptions
    "StepError",
    "OrchestratorTimeoutError",
    "StateError",
    "DependencyResolutionError",
    "ConcurrencyError",
    # Workflow helpers
    "chain",
    "parallel",
    "fan_out_fan_in",
    # Runners
    "run_script",
    "run_function",
    "ParallelRunner",
    "BatchRunner",
    "ExecutionResult",
    "run_parallel",
    "run_parallel_async",
    # Async runner (Stream 5)
    "AsyncParallelRunner",
    "AsyncTaskResult",
    "AsyncExecutionResult",
    # Async scheduler (Stream 5)
    "AsyncScheduler",
    "AsyncJob",
    "AsyncJobStatus",
    "SchedulerMetrics",
    # Retry decorator (Stream 5)
    "with_retry",
    # Thin orchestration
    "run",
    "run_async",
    "pipe",
    "batch",
    "chain_scripts",
    "workflow",
    "step",
    "Steps",
    "StepResult",
    "shell",
    "python_func",
    "retry",
    "timeout",
    "condition",
    # Integration bridges
    "OrchestratorBridge",
    "CICDBridge",
    "AgentOrchestrator",
    "StageConfig",
    "PipelineConfig",
    "create_pipeline_workflow",
    "run_ci_stage",
    "run_agent_task",
    # Submodules
    "engines",
    "execution",
    "monitors",
    "observability",
    "resilience",
    "workflows",
]

