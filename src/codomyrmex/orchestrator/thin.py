"""Thin Orchestration Utilities.

High-level, composable utilities for rapid orchestration.

This module provides:
- One-liner workflow creation
- Composable task builders
- Quick execution helpers
- Pipeline utilities

Example usage:
    from codomyrmex.orchestrator.thin import run, pipe, batch, watch

    # Run a single script
    result = run("scripts/my_script.py")

    # Pipe commands
    result = pipe(["echo hello", "cat -", "wc -c"])

    # Batch execution
    result = batch(["script1.py", "script2.py", "script3.py"])
"""

from __future__ import annotations

import asyncio
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

# Re-export extracted submodules so ``from codomyrmex.orchestrator.thin import …``
# continues to work unchanged.
from ._batch_chain import batch, chain_scripts
from ._decorators import condition, retry, timeout
from ._shell_exec import pipe, shell
from .execution.parallel_runner import ExecutionResult
from .execution.runner import run_function, run_script
from .workflows.workflow import (
    RetryPolicy,
    Workflow,
)

__all__ = [
    "Steps",
    "batch",
    "chain_scripts",
    "condition",
    "pipe",
    "python_func",
    "retry",
    # Quick execution
    "run",
    "run_async",
    # Utilities
    "shell",
    "step",
    "timeout",
    # Workflow builders
    "workflow",
]


@dataclass
class StepResult:
    """Result from a workflow step."""

    success: bool
    value: Any = None
    error: str | None = None
    execution_time: float = 0.0


def run(
    target: str | Path,
    timeout: int = 60,
    args: list[str] | None = None,
    env: dict[str, str] | None = None,
    cwd: Path | None = None,
) -> dict[str, Any]:
    """Run a single script or command.

    Args:
        target: Script path or shell command
        timeout: Execution timeout
        args: Additional arguments
        env: Environment variables
        cwd: Working directory

    Returns:
        Execution result dictionary
    """
    target_path = Path(target)

    if target_path.exists() and target_path.suffix == ".py":
        return run_script(target_path, timeout=timeout, env=env, cwd=cwd)
    # Treat as shell command
    return shell(str(target), timeout=timeout, env=env, cwd=cwd)


async def run_async(
    target: str | Path, timeout: int = 60, args: list[str] | None = None
) -> dict[str, Any]:
    """Async version of run."""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(
        None, lambda: run(target, timeout=timeout, args=args)
    )


class Steps:
    """Fluent workflow builder for chaining steps."""

    def __init__(self, name: str = "workflow"):
        """Initialize steps builder."""
        self._workflow = Workflow(name=name)
        self._steps: list[str] = []

    def add(
        self,
        name: str,
        action: Callable,
        depends_on: list[str] | None = None,
        timeout: float | None = None,
        retry: int = 1,
    ) -> Steps:
        """Add a step to the workflow.

        Args:
            name: Step name
            action: Callable to execute
            depends_on: Dependencies (defaults to previous step)
            timeout: Step timeout
            retry: Number of retry attempts

        Returns:
            Self for chaining
        """
        if depends_on is None and self._steps:
            depends_on = [self._steps[-1]]

        retry_policy = RetryPolicy(max_attempts=retry) if retry > 1 else None

        self._workflow.add_task(
            name=name,
            action=action,
            dependencies=depends_on,
            timeout=timeout,
            retry_policy=retry_policy,
        )
        self._steps.append(name)
        return self

    def add_parallel(
        self, steps: list[tuple], depends_on: list[str] | None = None
    ) -> Steps:
        """Add parallel steps.

        Args:
            steps: list of (name, action) tuples
            depends_on: Common dependencies

        Returns:
            Self for chaining
        """
        if depends_on is None and self._steps:
            depends_on = [self._steps[-1]]

        for name, action in steps:
            self._workflow.add_task(name=name, action=action, dependencies=depends_on)
            self._steps.append(name)

        return self

    async def run(self) -> dict[str, Any]:
        """Execute the workflow.

        Returns:
            Workflow results
        """
        return await self._workflow.run()

    def run_sync(self) -> dict[str, Any]:
        """Execute the workflow synchronously.

        Returns:
            Workflow results
        """
        return asyncio.run(self._workflow.run())

    @property
    def workflow(self) -> Workflow:
        """Get the underlying workflow."""
        return self._workflow


def step(
    name: str,
    action: Callable | None = None,
    timeout: float | None = None,
    retry: int = 1,
):
    """Decorator to create a workflow step.

    Args:
        name: Step name
        action: Action callable (uses decorated function if None)
        timeout: Step timeout
        retry: Retry attempts

    Returns:
        Decorator function
    """

    def decorator(func):
        """Decorator."""
        func._step_name = name
        func._step_timeout = timeout
        func._step_retry = retry
        return func

    return decorator


def workflow(name: str = "workflow") -> Steps:
    """Create a new workflow builder.

    Args:
        name: Workflow name

    Returns:
        Steps builder
    """
    return Steps(name=name)


def python_func(
    func: Callable, args: tuple = (), kwargs: dict | None = None, timeout: int = 60
) -> dict[str, Any]:
    """Run a Python function with monitoring.

    Args:
        func: Function to run
        args: Positional arguments
        kwargs: Keyword arguments
        timeout: Execution timeout

    Returns:
        Result dictionary
    """
    return run_function(func, args=args, kwargs=kwargs or {}, timeout=timeout)
