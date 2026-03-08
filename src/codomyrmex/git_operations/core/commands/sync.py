import os
import subprocess

from codomyrmex.logging_monitoring import get_logger
from codomyrmex.model_context_protocol.decorators import mcp_tool

from .branching import get_current_branch

_GIT_TIMEOUT = 120  # seconds

logger = get_logger(__name__)


@mcp_tool(name="git_push")
def push_changes(
    remote: str = "origin",
    branch: str | None = None,
    repository_path: str | None = None,
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
        logger.info("Pushing changes to %s/%s", remote, branch)

        subprocess.run(
            ["git", "push", remote, branch],
            cwd=repository_path,
            capture_output=True,
            text=True,
            check=True,
            timeout=_GIT_TIMEOUT,
        )

        logger.info("Changes pushed successfully")
        return True

    except subprocess.CalledProcessError as e:
        logger.error("Failed to push changes: %s", e)
        if e.stderr:
            logger.error("Git error: %s", e.stderr)
        return False
    except Exception as e:
        logger.error("Unexpected error pushing changes: %s", e)
        return False


@mcp_tool(name="git_pull")
def pull_changes(
    remote: str = "origin",
    branch: str | None = None,
    repository_path: str | None = None,
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
        logger.info("Pulling changes from %s/%s", remote, branch)

        subprocess.run(
            ["git", "pull", remote, branch],
            cwd=repository_path,
            capture_output=True,
            text=True,
            check=True,
            timeout=_GIT_TIMEOUT,
        )

        logger.info("Changes pulled successfully")
        return True

    except subprocess.CalledProcessError as e:
        logger.error("Failed to pull changes: %s", e)
        if e.stderr:
            logger.error("Git error: %s", e.stderr)
        return False
    except Exception as e:
        logger.error("Unexpected error pulling changes: %s", e)
        return False


@mcp_tool(name="git_fetch_changes")
def fetch_changes(
    remote: str = "origin",
    branch: str | None = None,
    repository_path: str | None = None,
    prune: bool = False,
) -> bool:
    """Fetch changes from a remote repository without merging."""
    if repository_path is None:
        repository_path = os.getcwd()

    try:
        logger.info("Fetching changes from %s", remote)

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
            timeout=_GIT_TIMEOUT,
        )

        logger.info("Successfully fetched changes from %s", remote)
        return True

    except subprocess.CalledProcessError as e:
        logger.error("Failed to fetch changes from %s: %s", remote, e)
        if e.stderr:
            logger.error("Git error: %s", e.stderr)
        return False
    except Exception as e:
        logger.error("Unexpected error fetching changes: %s", e)
        return False
