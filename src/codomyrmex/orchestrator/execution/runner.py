import multiprocessing
import os
import subprocess
import sys
import time
import traceback
from datetime import datetime
from pathlib import Path
from typing import Any

try:
    import resource

    RESOURCE_LIMIT_AVAILABLE = True
except ImportError:
    RESOURCE_LIMIT_AVAILABLE = False

from codomyrmex.logging_monitoring import get_logger

"""Script Runner.

Handles the actual execution of Python scripts.
"""
logger = get_logger(__name__)


def _set_memory_limit(memory_limit_mb: int):
    """Set memory limit for current process."""
    if not RESOURCE_LIMIT_AVAILABLE:
        return

    try:
        limit_bytes = memory_limit_mb * 1024 * 1024
        resource.setrlimit(resource.RLIMIT_AS, (limit_bytes, limit_bytes))
    except (ValueError, OSError) as e:
        logger.warning("Failed to set memory limit: %s", e)


def _find_project_root(script_path: Path) -> Path | None:
    """Climb directory tree to find the project root containing 'src'."""
    current_dir = script_path.parent
    for _ in range(5):
        if (current_dir / "src").exists():
            return current_dir
        if current_dir.parent == current_dir:
            break
        current_dir = current_dir.parent
    return None


def _build_run_env(
    env: dict[str, str] | None,
    script_config: dict[str, Any],
    script_path: Path,
) -> dict[str, str]:
    """Build the subprocess environment with PYTHONPATH configured."""
    run_env = os.environ.copy()
    if env:
        run_env.update(env)
    if "env" in script_config:
        run_env.update(script_config["env"])

    project_root = _find_project_root(script_path)
    if project_root:
        src_path = project_root / "src"
        scripts_root = project_root / "scripts"
        new_path = f"{src_path}:{scripts_root}"
        pythonpath = run_env.get("PYTHONPATH", "")
        run_env["PYTHONPATH"] = f"{new_path}:{pythonpath}" if pythonpath else new_path

    return run_env


def _execute_subprocess(
    cmd: list[str],
    timeout: int,
    cwd: Path,
    run_env: dict[str, str],
    allowed_exit_codes: list[int],
    memory_limit_mb: int | None,
) -> dict[str, Any]:
    """Run subprocess and return status/output dict."""
    partial: dict[str, Any] = {
        "exit_code": None,
        "stdout": "",
        "stderr": "",
        "status": "unknown",
        "error": None,
    }
    try:
        preexec = None
        if memory_limit_mb and RESOURCE_LIMIT_AVAILABLE:

            def preexec():
                return _set_memory_limit(memory_limit_mb)

        process = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=cwd,
            env=run_env,
            stdin=subprocess.DEVNULL,
            preexec_fn=preexec,
        )
        partial["exit_code"] = process.returncode
        partial["stdout"] = process.stdout
        partial["stderr"] = process.stderr
        partial["status"] = (
            "passed" if process.returncode in allowed_exit_codes else "failed"
        )
        if partial["status"] == "passed" and process.returncode != 0:
            partial["stdout"] += (
                f"\n[INFO] Script exited with code {process.returncode} (ALLOWED)"
            )
    except subprocess.TimeoutExpired as e:
        partial["status"] = "timeout"
        partial["error"] = f"Script timed out after {timeout}s"
        partial["stdout"] = e.stdout or ""
        partial["stderr"] = e.stderr or ""
    except (ValueError, RuntimeError, AttributeError, OSError, TypeError) as e:
        partial["status"] = "error"
        partial["error"] = str(e)
    return partial


def _init_script_result(script_path: Path) -> dict[str, Any]:
    """Build initial result skeleton for a script execution."""
    return {
        "script": str(script_path),
        "name": script_path.name,
        "subdirectory": script_path.parent.name,
        "start_time": datetime.now().isoformat(),
        "status": "unknown",
        "exit_code": None,
        "execution_time": 0.0,
        "stdout": "",
        "stderr": "",
        "error": None,
    }


def run_script(
    script_path: Path,
    timeout: int = 60,
    env: dict[str, str] | None = None,
    cwd: Path | None = None,
    config: dict[str, Any] | None = None,
    memory_limit_mb: int | None = None,
) -> dict[str, Any]:
    """Run a single script and capture output."""
    script_config = config or {}
    timeout = script_config.get("timeout", timeout)
    allowed_exit_codes = script_config.get("allowed_exit_codes", [0])
    result = _init_script_result(script_path)

    logger.info(
        "Script execution started: %s",
        script_path.name,
        extra={
            "event": "SCRIPT_START",
            "script": str(script_path),
            "subdirectory": script_path.parent.name,
        },
    )

    start_time = time.time()
    run_env = _build_run_env(env, script_config, script_path)
    cmd = [sys.executable, str(script_path), *script_config.get("args", [])]
    result.update(
        _execute_subprocess(
            cmd,
            timeout,
            cwd or script_path.parent,
            run_env,
            allowed_exit_codes,
            memory_limit_mb,
        )
    )
    result["execution_time"] = time.time() - start_time
    result["end_time"] = datetime.now().isoformat()

    logger.info(
        "Script execution completed: %s",
        script_path.name,
        extra={
            "event": "SCRIPT_END",
            "script": str(script_path),
            "subdirectory": script_path.parent.name,
            "status": result["status"],
            "exit_code": result["exit_code"],
            "execution_time": result["execution_time"],
        },
    )
    return result


def _target_wrapper(q, f, a, k, memory_limit_mb):
    """Wrapper to run function in separate process."""
    if memory_limit_mb:
        _set_memory_limit(memory_limit_mb)
    try:
        val = f(*a, **k)
        q.put(("success", val))
    except (ValueError, RuntimeError, AttributeError, OSError, TypeError):
        q.put(("error", traceback.format_exc()))


def _collect_queue_result(
    queue: multiprocessing.Queue, p: multiprocessing.Process
) -> dict[str, Any]:
    """Read the result placed by _target_wrapper into queue."""
    partial: dict[str, Any] = {"status": "unknown", "result": None, "error": None}
    try:
        status, val = queue.get(timeout=5)
        if status == "success":
            partial["status"] = "passed"
            partial["result"] = val
        else:
            partial["status"] = "error"
            partial["error"] = val
    except Exception:
        partial["status"] = "failed" if p.exitcode != 0 else "passed"
        if p.exitcode != 0:
            partial["error"] = f"Process exited with code {p.exitcode}"
    return partial


def run_function(
    func: callable,  # type: ignore
    args: tuple = (),
    kwargs: dict | None = None,
    timeout: int = 60,
    memory_limit_mb: int | None = None,
) -> dict[str, Any]:
    """Run a python function in a monitored separate process."""
    kwargs = kwargs or {}
    func_name = getattr(func, "__name__", "unknown_function")

    result: dict[str, Any] = {
        "name": func_name,
        "type": "function",
        "start_time": datetime.now().isoformat(),
        "status": "unknown",
        "execution_time": 0.0,
        "result": None,
        "error": None,
        "stdout": "",
    }

    queue: multiprocessing.Queue = multiprocessing.Queue()
    start_time = time.time()

    p = multiprocessing.Process(
        target=_target_wrapper, args=(queue, func, args, kwargs, memory_limit_mb)
    )
    p.start()
    p.join(timeout)

    if p.is_alive():
        p.terminate()
        p.join()
        result["status"] = "timeout"
        result["error"] = f"Function timed out after {timeout}s"
    else:
        result.update(_collect_queue_result(queue, p))

    result["execution_time"] = time.time() - start_time
    result["end_time"] = datetime.now().isoformat()
    return result
