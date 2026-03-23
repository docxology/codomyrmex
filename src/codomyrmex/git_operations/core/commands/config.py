import os
import subprocess

from codomyrmex.logging_monitoring import get_logger
from codomyrmex.model_context_protocol.decorators import mcp_tool

logger = get_logger(__name__)


@mcp_tool()
def get_config(
    key: str, repository_path: str | None = None, global_config: bool = False
) -> str | None:
    """Get a Git configuration value."""
    if repository_path is None:
        repository_path = os.getcwd()

    try:
        logger.debug("Getting Git config: %s", key)

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
            timeout=30,
        )

        value = result.stdout.strip()
        logger.debug("Config value for %s: %s", key, value)
        return value

    except subprocess.CalledProcessError:
        logger.debug("Config key '%s' not found or not set", key)
        return None
    except Exception as e:
        logger.error("Unexpected error getting config: %s", e)
        return None


@mcp_tool()
def set_config(
    key: str,
    value: str,
    repository_path: str | None = None,
    global_config: bool = False,
) -> bool:
    """set a Git configuration value."""
    if repository_path is None:
        repository_path = os.getcwd()

    try:
        logger.info("Setting Git config: %s = %s", key, value)

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
            timeout=30,
        )

        logger.info("Config '%s' set successfully", key)
        return True

    except subprocess.CalledProcessError as e:
        logger.error("Failed to set config '%s': %s", key, e)
        if e.stderr:
            logger.error("Git error: %s", e.stderr)
        return False
    except Exception as e:
        logger.error("Unexpected error setting config: %s", e)
        return False
