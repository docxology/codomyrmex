import os
import subprocess

from codomyrmex.logging_monitoring.core.logger_config import get_logger

logger = get_logger(__name__)

def get_config(key: str, repository_path: str = None, global_config: bool = False) -> str | None:
    """Get a Git configuration value."""
    if repository_path is None:
        repository_path = os.getcwd()

    try:
        logger.debug(f"Getting Git config: {key}")

        cmd = ["git", "config"]
        if global_config:
            cmd.append("--global")
        cmd.extend(["--get", key])

        result = subprocess.run(
            cmd,
            cwd=repository_path if not global_config else None,
            capture_output=True,
            text=True,
            check=True,
        )

        value = result.stdout.strip()
        logger.debug(f"Config value for {key}: {value}")
        return value

    except subprocess.CalledProcessError:
        logger.debug(f"Config key '{key}' not found or not set")
        return None
    except Exception as e:
        logger.error(f"Unexpected error getting config: {e}")
        return None

def set_config(
    key: str, value: str, repository_path: str = None, global_config: bool = False
) -> bool:
    """Set a Git configuration value."""
    if repository_path is None:
        repository_path = os.getcwd()

    try:
        logger.info(f"Setting Git config: {key} = {value}")

        cmd = ["git", "config"]
        if global_config:
            cmd.append("--global")
        cmd.extend([key, value])

        subprocess.run(
            cmd,
            cwd=repository_path if not global_config else None,
            capture_output=True,
            text=True,
            check=True,
        )

        logger.info(f"Config '{key}' set successfully")
        return True

    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to set config '{key}': {e}")
        if e.stderr:
            logger.error(f"Git error: {e.stderr}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error setting config: {e}")
        return False

