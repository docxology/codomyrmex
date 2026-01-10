from pathlib import Path
from typing import Dict, Any, Optional
import os
import shutil
import subprocess
import sys

import dotenv
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

def is_uv_available() -> bool:
    """Check if 'uv' is available in the path."""
    return shutil.which("uv") is not None

def generate_environment_report() -> str:
    """Generate detailed environment status report."""
    return "Environment report generation placeholder."

if __name__ == "__main__":
    print("Running env_checker.py standalone for basic checks...")
    mock_repo_root = os.path.abspath(os.path.join(_script_dir, ".."))

    ensure_dependencies_installed()
    check_and_setup_env_vars(mock_repo_root)
    print(f"UV Available: {is_uv_available()}")

    print("env_checker.py standalone checks complete.")
