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
from codomyrmex.validation.schemas import Result, ResultStatus

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
from .htn_planner import HTNPlanner, Method, Operator, State
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
from .swarm_topology import SwarmTopology, TaskSpec, TopologyMode
from .swarm_topology import TaskResult as SwarmTaskResult
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
                + "\n".join(
                    f"  - {name}" for name in ["default", "ci", "deploy", "test"]
                )
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
    "AgentOrchestrator",
    "AsyncExecutionResult",
    "AsyncJob",
    "AsyncJobStatus",
    "AsyncParallelRunner",
    # ── async execution ────────────────────────────────────────────────────────
    "AsyncScheduler",
    "AsyncTaskResult",
    "BatchRunner",
    "CICDBridge",
    "ConcurrencyError",
    "CycleError",
    "DependencyResolutionError",
    "ExecutionResult",
    "HTNPlanner",
    "Method",
    "Operator",
    # ── integration ────────────────────────────────────────────────────────────
    "OrchestratorBridge",
    "OrchestratorTimeoutError",
    "ParallelRunner",
    "PipelineConfig",
    "RetryPolicy",
    "SchedulerMetrics",
    "StageConfig",
    "State",
    "StateError",
    # ── exceptions ─────────────────────────────────────────────────────────────
    "StepError",
    "StepResult",
    "Steps",
    "SwarmTaskResult",
    # ── swarm topology ─────────────────────────────────────────────────────────
    "SwarmTopology",
    "Task",
    "TaskFailedError",
    "TaskResult",
    "TaskSpec",
    "TaskStatus",
    "TopologyMode",
    # ── workflow ───────────────────────────────────────────────────────────────
    "Workflow",
    "WorkflowError",
    "batch",
    "chain",
    "chain_scripts",
    # ── CLI integration ────────────────────────────────────────────────────────
    "cli_commands",
    "condition",
    "create_pipeline_workflow",
    "discover_scripts",
    "engines",
    "execution",
    "fan_out_fan_in",
    "get_script_config",
    "load_config",
    "monitors",
    "observability",
    "parallel",
    "pipe",
    "pipelines",
    "python_func",
    "resilience",
    "retry",
    # ── thin orchestration DSL ─────────────────────────────────────────────────
    "run",
    "run_agent_task",
    "run_async",
    "run_ci_stage",
    "run_function",
    # ── runners ────────────────────────────────────────────────────────────────
    "run_orchestrator",
    "run_parallel",
    "run_parallel_async",
    "run_script",
    # ── submodules ─────────────────────────────────────────────────────────────
    "scheduler",
    "shell",
    "state",
    "step",
    "templates",
    "timeout",
    "triggers",
    "with_retry",
    "workflow",
    "workflows",
]
