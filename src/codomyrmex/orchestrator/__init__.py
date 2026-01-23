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
"""

from .core import main as run_orchestrator
from .config import load_config, get_script_config
from .workflow import (
    Workflow,
    Task,
    TaskStatus,
    TaskResult,
    RetryPolicy,
    WorkflowError,
    CycleError,
    TaskFailedError,
    chain,
    parallel,
    fan_out_fan_in,
)
from .exceptions import (
    StepError,
    OrchestratorTimeoutError,
    StateError,
    DependencyResolutionError,
    ConcurrencyError,
)
from .runner import run_script, run_function
from .parallel_runner import (
    ParallelRunner,
    BatchRunner,
    ExecutionResult,
    run_parallel,
    run_parallel_async,
)
from .discovery import discover_scripts
from .thin import (
    run,
    run_async,
    pipe,
    batch,
    chain_scripts,
    workflow,
    step,
    Steps,
    shell,
    python_func,
    retry,
    timeout,
    condition,
    StepResult,
)
from .integration import (
    OrchestratorBridge,
    CICDBridge,
    AgentOrchestrator,
    StageConfig,
    PipelineConfig,
    create_pipeline_workflow,
    run_ci_stage,
    run_agent_task,
)

__all__ = [
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
]
