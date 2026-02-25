import os
import subprocess

from codomyrmex.logging_monitoring.core.logger_config import get_logger
from codomyrmex.model_context_protocol.decorators import mcp_tool

from .branching import get_current_branch

logger = get_logger(__name__)

@mcp_tool()
def push_changes(
    remote: str = "origin", branch: str = None, repository_path: str = None
) -> bool:
    """Push committed changes to a remote repository."""
    if repository_path is None:
        repository_path = os.getcwd()

    if branch is None:
        branch = get_current_branch(repository_path)
        if not branch:
            logger.error("Could not determine current branch for push")
            return False

    try:
        logger.info(f"Pushing changes to {remote}/{branch}")

        subprocess.run(
            ["git", "push", remote, branch],
            cwd=repository_path,
            capture_output=True,
            text=True,
            check=True,
        )

        logger.info("Changes pushed successfully")
        return True

    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to push changes: {e}")
        if e.stderr:
            logger.error(f"Git error: {e.stderr}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error pushing changes: {e}")
        return False

@mcp_tool()
def pull_changes(
    remote: str = "origin", branch: str = None, repository_path: str = None
) -> bool:
    """Pull changes from a remote repository."""
    if repository_path is None:
        repository_path = os.getcwd()

    if branch is None:
        branch = get_current_branch(repository_path)
        if not branch:
            logger.error("Could not determine current branch for pull")
            return False

    try:
        logger.info(f"Pulling changes from {remote}/{branch}")

        subprocess.run(
            ["git", "pull", remote, branch],
            cwd=repository_path,
            capture_output=True,
            text=True,
            check=True,
        )

        logger.info("Changes pulled successfully")
        return True

    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to pull changes: {e}")
        if e.stderr:
            logger.error(f"Git error: {e.stderr}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error pulling changes: {e}")
        return False

def fetch_changes(
    remote: str = "origin",
    branch: str = None,
    repository_path: str = None,
    prune: bool = False,
) -> bool:
    """Fetch changes from a remote repository without merging."""
    if repository_path is None:
        repository_path = os.getcwd()

    try:
        logger.info(f"Fetching changes from {remote}")

        cmd = ["git", "fetch"]
        if prune:
            cmd.append("--prune")
        cmd.append(remote)
        if branch:
            cmd.append(branch)

        subprocess.run(
            cmd,
            cwd=repository_path,
            capture_output=True,
            text=True,
            check=True,
        )

        logger.info(f"Successfully fetched changes from {remote}")
        return True

    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to fetch changes from {remote}: {e}")
        if e.stderr:
            logger.error(f"Git error: {e.stderr}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error fetching changes: {e}")
        return False

