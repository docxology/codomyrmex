from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
import os
import subprocess
import sys
import time

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


def run_script(
    script_path: Path,
    timeout: int = 60,
    env: Optional[Dict[str, str]] = None,
    cwd: Optional[Path] = None,
    config: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Run a single script and capture output.
    
    Args:
        script_path: Path to the script
        timeout: Timeout in seconds
        env: Environment variables
        cwd: Working directory
        config: Script configuration
        
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
    project_root = script_path.parent.parent.parent
    src_path = project_root / "src"
    
    # If we are running from installed package, we might not need this, but for dev it helps
    if src_path.exists():
        pythonpath = run_env.get("PYTHONPATH", "")
        # Add scripts root to path as well to allow scripts to import from sibling scripts if needed (though discouraged)
        scripts_root = project_root / "scripts"
        new_path = f"{src_path}:{scripts_root}"
        run_env["PYTHONPATH"] = f"{new_path}:{pythonpath}" if pythonpath else new_path
    
    # get args from config
    script_args = script_config.get("args", [])
    cmd = [sys.executable, str(script_path)] + script_args
    print(f"DEBUG: src_path={src_path}, PYTHONPATH={run_env.get("PYTHONPATH")}")

    try:
        process = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=cwd or script_path.parent,
            env=run_env,
            stdin=subprocess.DEVNULL,
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
    
    return result
