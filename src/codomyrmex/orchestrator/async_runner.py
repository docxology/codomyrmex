# DEPRECATED(v0.2.0): Shim module. Import from orchestrator.execution.async_runner instead. Will be removed in v0.3.0.
"""Backward-compatibility shim. Canonical location: orchestrator.execution.async_runner"""
from .execution.async_runner import *  # noqa: F401,F403
from .execution.async_runner import (
    AsyncParallelRunner,
    AsyncTaskResult,
    AsyncExecutionResult,
)
