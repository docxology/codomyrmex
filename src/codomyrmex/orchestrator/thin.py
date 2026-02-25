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

import asyncio
import os
import subprocess
import time
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from codomyrmex.logging_monitoring import get_logger

from .execution.parallel_runner import ExecutionResult, run_parallel
from .execution.runner import run_function, run_script
from .workflows.workflow import (
    RetryPolicy,
    Workflow,
)

logger = get_logger(__name__)

__all__ = [
    # Quick execution
    "run",
    "run_async",
    "pipe",
    "batch",
    "chain_scripts",
    # Workflow builders
    "workflow",
    "step",
    "Steps",
    # Utilities
    "shell",
    "python_func",
    "retry",
    "timeout",
    "condition",
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
    args: list[str] = None,
    env: dict[str, str] = None,
    cwd: Path = None
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
    else:
        # Treat as shell command
        return shell(str(target), timeout=timeout, env=env, cwd=cwd)


async def run_async(
    target: str | Path,
    timeout: int = 60,
    args: list[str] = None
) -> dict[str, Any]:
    """Async version of run."""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(
        None,
        lambda: run(target, timeout=timeout, args=args)
    )


def shell(
    command: str,
    timeout: int = 60,
    env: dict[str, str] = None,
    cwd: Path = None,
    check: bool = False
) -> dict[str, Any]:
    """Execute a shell command.

    Args:
        command: Shell command to execute
        timeout: Execution timeout
        env: Additional environment variables
        cwd: Working directory
        check: Raise exception on non-zero exit

    Returns:
        Result dictionary with stdout, stderr, returncode
    """
    run_env = os.environ.copy()
    if env:
        run_env.update(env)

    start_time = time.time()

    try:
        result = subprocess.run(
            command,
            shell=True,  # SECURITY: Intentional — shell() is a named shell executor utility
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=cwd,
            env=run_env
        )

        output = {
            "success": result.returncode == 0,
            "command": command,
            "returncode": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "execution_time": time.time() - start_time
        }

        if check and result.returncode != 0:
            raise subprocess.CalledProcessError(
                result.returncode, command, result.stdout, result.stderr
            )

        return output

    except subprocess.TimeoutExpired as e:
        return {
            "success": False,
            "command": command,
            "returncode": None,
            "error": f"Timeout after {timeout}s",
            "stdout": e.stdout or "",
            "stderr": e.stderr or "",
            "execution_time": timeout
        }
    except (ValueError, RuntimeError, AttributeError, OSError, TypeError) as e:
        return {
            "success": False,
            "command": command,
            "error": str(e),
            "execution_time": time.time() - start_time
        }


def pipe(
    commands: list[str],
    timeout_per_command: int = 30,
    stop_on_error: bool = True
) -> dict[str, Any]:
    """Pipe commands together sequentially.

    Args:
        commands: List of shell commands
        timeout_per_command: Timeout for each command
        stop_on_error: Stop on first error

    Returns:
        Result with all command outputs
    """
    results = []
    prev_stdout = ""
    overall_success = True
    start_time = time.time()

    for i, cmd in enumerate(commands):
        # Set previous output as input via environment
        env = {"PIPE_INPUT": prev_stdout, "PIPE_INDEX": str(i)}

        result = shell(cmd, timeout=timeout_per_command, env=env)
        results.append(result)

        if result["success"]:
            prev_stdout = result.get("stdout", "")
        else:
            overall_success = False
            if stop_on_error:
                break

    return {
        "success": overall_success,
        "commands": len(commands),
        "completed": len(results),
        "results": results,
        "final_output": prev_stdout,
        "execution_time": time.time() - start_time
    }


def batch(
    targets: list[str | Path],
    workers: int = None,
    timeout: int = 60
) -> ExecutionResult:
    """Run multiple targets in parallel.

    Args:
        targets: List of script paths or commands
        workers: Number of parallel workers
        timeout: Timeout per target

    Returns:
        ExecutionResult with aggregated results
    """
    scripts = []
    for target in targets:
        target_path = Path(target)
        if target_path.exists():
            scripts.append(target_path)

    if not scripts:
        return ExecutionResult()

    return run_parallel(
        scripts=scripts,
        max_workers=workers,
        timeout=timeout
    )


def chain_scripts(
    scripts: list[str | Path],
    timeout_per_script: int = 60,
    pass_results: bool = True,
    stop_on_error: bool = True
) -> dict[str, Any]:
    """Chain scripts sequentially with result passing.

    Args:
        scripts: List of script paths
        timeout_per_script: Timeout per script
        pass_results: Pass previous results via environment
        stop_on_error: Stop on first failure

    Returns:
        Result dictionary
    """
    import json

    results = []
    prev_result = None
    overall_success = True
    start_time = time.time()

    for script in scripts:
        script_path = Path(script)
        if not script_path.exists():
            results.append({"script": str(script), "error": "Not found", "success": False})
            if stop_on_error:
                overall_success = False
                break
            continue

        env = {}
        if pass_results and prev_result:
            env["PREV_RESULT"] = json.dumps(prev_result)
            env["PREV_SUCCESS"] = str(prev_result.get("success", False))

        result = run_script(script_path, timeout=timeout_per_script, env=env)
        results.append(result)

        if result.get("status") != "passed":
            overall_success = False
            if stop_on_error:
                break

        prev_result = result

    return {
        "success": overall_success,
        "scripts": len(scripts),
        "completed": len(results),
        "passed": sum(1 for r in results if r.get("status") == "passed"),
        "results": results,
        "execution_time": time.time() - start_time
    }


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
        depends_on: list[str] = None,
        timeout: float = None,
        retry: int = 1
    ) -> "Steps":
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
            retry_policy=retry_policy
        )
        self._steps.append(name)
        return self

    def add_parallel(
        self,
        steps: list[tuple],
        depends_on: list[str] = None
    ) -> "Steps":
        """Add parallel steps.

        Args:
            steps: List of (name, action) tuples
            depends_on: Common dependencies

        Returns:
            Self for chaining
        """
        if depends_on is None and self._steps:
            depends_on = [self._steps[-1]]

        for name, action in steps:
            self._workflow.add_task(
                name=name,
                action=action,
                dependencies=depends_on
            )
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
    action: Callable = None,
    timeout: float = None,
    retry: int = 1
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
        """Execute Decorator operations natively."""
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
    func: Callable,
    args: tuple = (),
    kwargs: dict = None,
    timeout: int = 60
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


def retry(
    action: Callable,
    max_attempts: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0
) -> Callable:
    """Wrap an action with retry logic.

    Args:
        action: Action to wrap
        max_attempts: Maximum retry attempts
        delay: Initial delay between retries
        backoff: Backoff multiplier

    Returns:
        Wrapped action
    """
    async def wrapper(*args, **kwargs):
        last_error = None
        current_delay = delay

        for attempt in range(1, max_attempts + 1):
            try:
                if asyncio.iscoroutinefunction(action):
                    return await action(*args, **kwargs)
                else:
                    return action(*args, **kwargs)
            except (ValueError, RuntimeError, AttributeError, OSError, TypeError) as e:
                last_error = e
                if attempt < max_attempts:
                    logger.warning(f"Attempt {attempt} failed, retrying in {current_delay}s: {e}")
                    await asyncio.sleep(current_delay)
                    current_delay *= backoff

        raise last_error

    return wrapper


def timeout(seconds: float) -> Callable:
    """Decorator to add timeout to an action.

    Args:
        seconds: Timeout in seconds

    Returns:
        Decorator function
    """
    def decorator(action):
        """Execute Decorator operations natively."""
        async def wrapper(*args, **kwargs):
            if asyncio.iscoroutinefunction(action):
                return await asyncio.wait_for(
                    action(*args, **kwargs),
                    timeout=seconds
                )
            else:
                loop = asyncio.get_event_loop()
                return await asyncio.wait_for(
                    loop.run_in_executor(None, lambda: action(*args, **kwargs)),
                    timeout=seconds
                )
        return wrapper
    return decorator


def condition(predicate: Callable[[dict], bool]) -> Callable:
    """Create a condition function for conditional task execution.

    Args:
        predicate: Function that receives task results and returns bool

    Returns:
        Condition function
    """
    return predicate
