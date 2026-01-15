from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
import os
import subprocess
import signal
import sys
import time
import multiprocessing
import traceback
try:
    import resource
    RESOURCE_LIMIT_AVAILABLE = True
except ImportError:
    RESOURCE_LIMIT_AVAILABLE = False

from codomyrmex.logging_monitoring import get_logger























"""Script Runner.

Handles the actual execution of Python scripts.

This module provides runner functionality including:
- 1 functions: run_script
- 0 classes: 

Usage:
    from runner import FunctionName, ClassName
    # Example usage here
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
        logger.warning(f"Failed to set memory limit: {e}")

def run_script(
    script_path: Path,
    timeout: int = 60,
    env: Optional[Dict[str, str]] = None,
    cwd: Optional[Path] = None,
    config: Optional[Dict[str, Any]] = None,
    memory_limit_mb: Optional[int] = None,
) -> Dict[str, Any]:
    """
    Run a single script and capture output.
    
    Args:
        script_path: Path to the script
        script_path: Path to the script
        timeout: Timeout in seconds
        env: Environment variables
        cwd: Working directory
        config: Script configuration
        memory_limit_mb: Optional memory limit in MB (Unix only)
        
    Returns:
        Execution result dictionary
    """
    script_config = config or {}
    timeout = script_config.get("timeout", timeout)
    allowed_exit_codes = script_config.get("allowed_exit_codes", [0])
    
    result = {
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
    
    start_time = time.time()
    
    # Prepare environment
    run_env = os.environ.copy()
    if env:
        run_env.update(env)
    
    # Merge env from config
    if "env" in script_config:
        run_env.update(script_config["env"])
    
    # Add project src to PYTHONPATH
    # Assuming standard structure where scripts is at root/scripts and src is at root/src
    # script_path -> subdir -> scripts -> root
    # Add project src to PYTHONPATH
    # Robustly find project root by searching for 'src' directory
    current_dir = script_path.parent
    project_root = None
    
    # Climb up to 5 levels to find project root containing 'src'
    for _ in range(5):
        if (current_dir / "src").exists():
            project_root = current_dir
            break
        if current_dir.parent == current_dir: # Root reached
            break
        current_dir = current_dir.parent
        
    if project_root:
        src_path = project_root / "src"
        pythonpath = run_env.get("PYTHONPATH", "")
        # Add scripts root to path as well
        scripts_root = project_root / "scripts"
        new_path = f"{src_path}:{scripts_root}"
        run_env["PYTHONPATH"] = f"{new_path}:{pythonpath}" if pythonpath else new_path
        
        # Also ensure sys.executable is used from environment if available
        # or stick to sys.executable from current process
    else:
        # Fallback for when src is not found relative to script
        # This logs a warning but continues
        if env and env.get("PYTHONPATH"):
             pass # External env configured
        else:
             pass # Removed DEBUG print statement
    
    # get args from config
    script_args = script_config.get("args", [])
    cmd = [sys.executable, str(script_path)] + script_args
    # Debug logging removed - use --verbose flag for detailed output

    try:
        # Prepare preexec_fn for memory limit
        preexec = None
        if memory_limit_mb and RESOURCE_LIMIT_AVAILABLE:
            preexec = lambda: _set_memory_limit(memory_limit_mb)
            
        process = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=cwd or script_path.parent,
            env=run_env,
            stdin=subprocess.DEVNULL,
            preexec_fn=preexec,
        )
        
        result["exit_code"] = process.returncode
        result["stdout"] = process.stdout
        result["stderr"] = process.stderr
        result["status"] = "passed" if process.returncode in allowed_exit_codes else "failed"
        
        if result["status"] == "passed" and process.returncode != 0:
             # Annotate passed (non-zero)
             result["stdout"] += f"\n[INFO] Script exited with code {process.returncode} (ALLOWED)"
        
    except subprocess.TimeoutExpired as e:
        result["status"] = "timeout"
        result["error"] = f"Script timed out after {timeout}s"
        result["stdout"] = e.stdout if e.stdout else ""
        result["stderr"] = e.stderr if e.stderr else ""
        
    except Exception as e:
        result["status"] = "error"
        result["error"] = str(e)
    
    result["execution_time"] = time.time() - start_time
    result["end_time"] = datetime.now().isoformat()
    
    result["end_time"] = datetime.now().isoformat()
    
    return result

def _target_wrapper(q, f, a, k, memory_limit_mb):
    """Wrapper to run function in separate process."""
    if memory_limit_mb:
        _set_memory_limit(memory_limit_mb)
    try:
        val = f(*a, **k)
        q.put(("success", val))
    except Exception:
        q.put(("error", traceback.format_exc()))

def run_function(
    func: callable,
    args: tuple = (),
    kwargs: dict = None,
    timeout: int = 60,
    memory_limit_mb: Optional[int] = None,
) -> Dict[str, Any]:
    """
    Run a python function in a monitored separate process.
    
    Args:
        func: Function to run
        args: Positional arguments
        kwargs: Keyword arguments
        timeout: Timeout in seconds
        memory_limit_mb: Optional memory limit
        
    Returns:
        Execution result dictionary
    """
    kwargs = kwargs or {}
    func_name = getattr(func, "__name__", "unknown_function")
    
    result = {
        "name": func_name,
        "type": "function",
        "start_time": datetime.now().isoformat(),
        "status": "unknown",
        "execution_time": 0.0,
        "result": None,
        "error": None,
        "stdout": "", # Capturing stdout from functon complicates things with multiprocessing
    }
    
    queue = multiprocessing.Queue()
    start_time = time.time()
    
    p = multiprocessing.Process(
        target=_target_wrapper, 
        args=(queue, func, args, kwargs, memory_limit_mb)
    )
    p.start()
    p.join(timeout)
    
    if p.is_alive():
        p.terminate()
        p.join()
        result["status"] = "timeout"
        result["error"] = f"Function timed out after {timeout}s"
    else:
        if not queue.empty():
            status, val = queue.get()
            if status == "success":
                result["status"] = "passed"
                result["result"] = val
            else:
                result["status"] = "error"
                result["error"] = val
        else:
            # Succeeded but no return? or crashed silently?
            if p.exitcode != 0:
                 result["status"] = "failed"
                 result["error"] = f"Process exited with code {p.exitcode}"
            else:
                 result["status"] = "passed"

    result["execution_time"] = time.time() - start_time
    result["end_time"] = datetime.now().isoformat()
    
    return result
