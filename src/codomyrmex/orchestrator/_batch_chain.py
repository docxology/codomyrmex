"""Batch and chain execution utilities for thin orchestration.

Provides ``batch`` (parallel script execution) and ``chain_scripts``
(sequential execution with result passing).

These were extracted from ``thin.py`` to keep each module focused.
"""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

from .execution.parallel_runner import ExecutionResult, run_parallel
from .execution.runner import run_script

__all__ = [
    "batch",
    "chain_scripts",
]


def batch(
    targets: list[str | Path], workers: int | None = None, timeout: int = 60
) -> ExecutionResult:
    """Run multiple targets in parallel.

    Args:
        targets: list of script paths or commands
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

    return run_parallel(scripts=scripts, max_workers=workers, timeout=timeout)


def chain_scripts(
    scripts: list[str | Path],
    timeout_per_script: int = 60,
    pass_results: bool = True,
    stop_on_error: bool = True,
) -> dict[str, Any]:
    """Chain scripts sequentially with result passing.

    Args:
        scripts: list of script paths
        timeout_per_script: Timeout per script
        pass_results: Pass previous results via environment
        stop_on_error: Stop on first failure

    Returns:
        Result dictionary
    """
    results: list[dict[str, Any]] = []
    prev_result: dict[str, Any] | None = None
    overall_success = True
    start_time = time.time()

    for script in scripts:
        script_path = Path(script)
        if not script_path.exists():
            results.append(
                {"script": str(script), "error": "Not found", "success": False}
            )
            overall_success = False
            if stop_on_error:
                break
            continue

        env: dict[str, str] = {}
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
        "execution_time": time.time() - start_time,
    }
