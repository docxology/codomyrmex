"""Shell execution utilities for thin orchestration.

Provides the ``shell`` function and the ``pipe`` command-chaining
helper — both return command-result dicts rather than raising on
process failure (intentional "command result object" contract).

These were extracted from ``thin.py`` to keep each module focused.
"""

from __future__ import annotations

import os
import subprocess
import time
from typing import Any

__all__ = [
    "pipe",
    "shell",
]


def shell(
    command: str,
    timeout: int = 60,
    env: dict[str, str] | None = None,
    cwd: Any = None,
    check: bool = False,
) -> dict[str, Any]:
    """Execute a shell command.

    This function always returns a dict — it never raises on process failure
    or timeout (unless ``check=True``). Callers must inspect ``result["success"]``
    to detect errors.  This is an intentional "command result object" contract
    so orchestration pipelines can aggregate outcomes without try/except at every
    call site.

    Args:
        command: Shell command to execute
        timeout: Execution timeout
        env: Additional environment variables
        cwd: Working directory
        check: If True, raise :class:`subprocess.CalledProcessError` on non-zero exit.
            All other errors (timeout, OS error) still return a dict.

    Returns:
        dict with keys:
            - ``success`` (bool): True if returncode == 0
            - ``command`` (str): The original command string
            - ``returncode`` (int | None): Exit code, or None on timeout
            - ``stdout`` (str): Captured stdout (empty string on error)
            - ``stderr`` (str): Captured stderr (empty string on error)
            - ``execution_time`` (float): Elapsed seconds
            - ``error`` (str): Human-readable error description (timeout/OS errors only)
    """
    run_env = os.environ.copy()
    if env:
        run_env.update(env)

    start_time = time.time()

    try:
        result = subprocess.run(  # noqa: S603
            command,
            shell=True,  # SECURITY: Intentional — shell() is a named shell executor utility  # noqa: S602
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=cwd,
            env=run_env,
            check=False,
        )

        output = {
            "success": result.returncode == 0,
            "command": command,
            "returncode": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "execution_time": time.time() - start_time,
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
            "execution_time": timeout,
        }
    except (ValueError, RuntimeError, AttributeError, OSError, TypeError) as e:
        return {
            "success": False,
            "command": command,
            "returncode": None,
            "error": str(e),
            "stdout": "",
            "stderr": "",
            "execution_time": time.time() - start_time,
        }


def pipe(
    commands: list[str], timeout_per_command: int = 30, stop_on_error: bool = True
) -> dict[str, Any]:
    """Pipe commands together sequentially.

    Args:
        commands: list of shell commands
        timeout_per_command: Timeout for each command
        stop_on_error: Stop on first error

    Returns:
        Result with all command outputs
    """
    results: list[dict[str, Any]] = []
    prev_stdout = ""
    overall_success = True
    start_time = time.time()

    for i, cmd in enumerate(commands):
        # set previous output as input via environment
        pipe_env = {"PIPE_INPUT": prev_stdout, "PIPE_INDEX": str(i)}

        result = shell(cmd, timeout=timeout_per_command, env=pipe_env)
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
        "execution_time": time.time() - start_time,
    }
