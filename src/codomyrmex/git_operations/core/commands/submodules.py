import os
import subprocess

from codomyrmex.logging_monitoring.core.logger_config import get_logger

logger = get_logger(__name__)

def init_submodules(repository_path: str = None) -> bool:
    """Initialize and update submodules."""
    if repository_path is None:
        repository_path = os.getcwd()

    try:
        logger.info(f"Initializing submodules in {repository_path}")
        subprocess.run(
            ["git", "submodule", "update", "--init", "--recursive"],
            cwd=repository_path,
            capture_output=True,
            text=True,
            check=True,
        )
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to init submodules: {e}")
        return False

def update_submodules(repository_path: str = None) -> bool:
    """Update submodules to latest commit."""
    if repository_path is None:
        repository_path = os.getcwd()

    try:
        logger.info(f"Updating submodules in {repository_path}")
        subprocess.run(
            ["git", "submodule", "update", "--remote", "--recursive"],
            cwd=repository_path,
            capture_output=True,
            text=True,
            check=True,
        )
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to update submodules: {e}")
        return False

