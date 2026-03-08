import os
import subprocess

from codomyrmex.logging_monitoring import get_logger
from codomyrmex.model_context_protocol.decorators import mcp_tool

logger = get_logger(__name__)


@mcp_tool()
def init_submodules(repository_path: str | None = None) -> bool:
    """Initialize and update submodules."""
    if repository_path is None:
        repository_path = os.getcwd()

    try:
        logger.info("Initializing submodules in %s", repository_path)
        subprocess.run(
            ["git", "submodule", "update", "--init", "--recursive"],
            cwd=repository_path,
            capture_output=True,
            text=True,
            check=True,
        )
        return True
    except subprocess.CalledProcessError as e:
        logger.error("Failed to init submodules: %s", e)
        if e.stderr:
            logger.error("Git error: %s", e.stderr)
        return False
    except Exception as e:
        logger.error("Unexpected error initializing submodules: %s", e)
        return False


@mcp_tool()
def update_submodules(repository_path: str | None = None) -> bool:
    """Update submodules to latest commit."""
    if repository_path is None:
        repository_path = os.getcwd()

    try:
        logger.info("Updating submodules in %s", repository_path)
        subprocess.run(
            ["git", "submodule", "update", "--remote", "--recursive"],
            cwd=repository_path,
            capture_output=True,
            text=True,
            check=True,
        )
        return True
    except subprocess.CalledProcessError as e:
        logger.error("Failed to update submodules: %s", e)
        if e.stderr:
            logger.error("Git error: %s", e.stderr)
        return False
    except Exception as e:
        logger.error("Unexpected error updating submodules: %s", e)
        return False
