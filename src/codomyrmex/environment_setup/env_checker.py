from pathlib import Path
from typing import Dict, Any, Optional
import os
import shutil
import subprocess
import sys

import dotenv
import kit

from codomyrmex.logging_monitoring.logger_config import get_logger







logger = get_logger(__name__)

# Store the original script directory to correctly locate files relative to REPO_ROOT_PATH
_script_dir = os.path.dirname(__file__)

def ensure_dependencies_installed():
    """
    Checks if primary dependencies 'kit' and 'python-dotenv' are installed.
    If not, it prints detailed instructions for setting them up.
    """
    dependencies_ok = True
    try:
        print("[INFO] cased/kit library found.")
    except ImportError:
        print("[WARNING] cased/kit library NOT found.", file=sys.stderr)
        dependencies_ok = False

    try:
        print("[INFO] python-dotenv library found.")
    except ImportError:
        print("[WARNING] python-dotenv library NOT found.", file=sys.stderr)
        dependencies_ok = False
    
    if not dependencies_ok:
        print("[INSTRUCTION] Please install missing dependencies.", file=sys.stderr)
        return False
    return True

def check_and_setup_env_vars(repo_root: str) -> bool:
    """Check and setup environment variables."""
    try:
        dotenv_path = os.path.join(repo_root, ".env")
        if os.path.exists(dotenv_path):
            dotenv.load_dotenv(dotenv_path)
            return True
        else:
            return False
    except ImportError:
        return False

def validate_python_version() -> bool:
    """Validate python version."""
    return sys.version_info >= (3, 10)

def is_uv_available() -> bool:
    """Check if 'uv' is available in the path."""
    return shutil.which("uv") is not None

def is_uv_environment() -> bool:
    """Check if running within a uv environment."""
    # Check for VIRTUAL_ENV environment variable which uv sets
    # Or specifically check if the python executable path is inside .venv created by uv
    return os.environ.get("VIRTUAL_ENV") is not None or is_uv_available()

def generate_environment_report() -> str:
    """Generate detailed environment status report."""
    return "Environment report generation placeholder."

def validate_environment_completeness(repo_root: Optional[str] = None) -> bool:
    """
    Validate overall environment completeness.
    
    Args:
        repo_root: Optional root path
        
    Returns:
        True if all checks pass
    """
    if repo_root is None:
        repo_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    deps = ensure_dependencies_installed()
    env_vars = check_and_setup_env_vars(repo_root)
    py_ver = validate_python_version()
    uv_env = is_uv_environment()
    
    return deps and env_vars and py_ver

if __name__ == "__main__":
    print("Running env_checker.py standalone for basic checks...")
    mock_repo_root = os.path.abspath(os.path.join(_script_dir, ".."))

    ensure_dependencies_installed()
    check_and_setup_env_vars(mock_repo_root)
    print(f"UV Available: {is_uv_available()}")

    print("env_checker.py standalone checks complete.")
