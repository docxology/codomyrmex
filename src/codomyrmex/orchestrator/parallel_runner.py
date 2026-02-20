# DEPRECATED(v0.2.0): Shim module. Import from orchestrator.execution.parallel_runner instead. Will be removed in v0.3.0.
"""Backward-compatibility shim. Canonical location: orchestrator.execution.parallel_runner"""
from .execution.parallel_runner import *  # noqa: F401,F403
from .execution.parallel_runner import (
    BatchRunner,
    ExecutionResult,
    ParallelRunner,
    run_parallel,
    run_parallel_async,
)
