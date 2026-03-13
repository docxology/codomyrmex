import os
import subprocess

from codomyrmex.logging_monitoring import get_logger
from codomyrmex.model_context_protocol.decorators import mcp_tool

from .branching import get_current_branch, switch_branch

_GIT_TIMEOUT = 60  # seconds

logger = get_logger(__name__)


@mcp_tool(name="git_merge")
def merge_branch(
    source_branch: str,
    target_branch: str | None = None,
    repository_path: str | None = None,
    strategy: str | None = None,
) -> bool:
    """Merge a source branch into the target branch."""
    if repository_path is None:
        repository_path = os.getcwd()

    if target_branch is None:
        target_branch = get_current_branch(repository_path)
        if not target_branch:
            logger.error("Could not determine target branch for merge")
            return False

    try:
        logger.info(
            "Merging branch '%s' into '%s' in %s",
            source_branch,
            target_branch,
            repository_path,
        )

        # Switch to target branch first
        if not switch_branch(target_branch, repository_path):
            logger.error("Could not switch to target branch '%s'", target_branch)
            return False

        # Prepare merge command
        cmd = ["git", "merge", "--no-edit"]
        if strategy:
            cmd.extend(["-s", strategy])
        cmd.append(source_branch)

        subprocess.run(
            cmd,
            cwd=repository_path,
            capture_output=True,
            text=True,
            check=True,
            timeout=_GIT_TIMEOUT,
        )

        logger.info("Successfully merged '%s' into '%s'", source_branch, target_branch)
        return True

    except subprocess.CalledProcessError as e:
        logger.error("Failed to merge branch '%s': %s", source_branch, e)
        if e.stderr:
            logger.error("Git error: %s", e.stderr)
        return False
    except Exception as e:
        logger.error("Unexpected error merging branch: %s", e)
        return False


@mcp_tool(name="git_rebase")
def rebase_branch(
    target_branch: str, repository_path: str | None = None, interactive: bool = False
) -> bool:
    """Rebase current branch onto target branch."""
    if repository_path is None:
        repository_path = os.getcwd()

    try:
        current_branch = get_current_branch(repository_path)
        logger.info(
            "Rebasing branch '%s' onto '%s' in %s",
            current_branch,
            target_branch,
            repository_path,
        )

        cmd = ["git", "rebase"]
        if interactive:
            cmd.append("-i")
        cmd.append(target_branch)

        subprocess.run(
            cmd,
            cwd=repository_path,
            capture_output=True,
            text=True,
            check=True,
            timeout=_GIT_TIMEOUT,
        )

        logger.info(
            "Successfully rebased '%s' onto '%s'", current_branch, target_branch
        )
        return True

    except subprocess.CalledProcessError as e:
        logger.error("Failed to rebase onto '%s': %s", target_branch, e)
        if e.stderr:
            logger.error("Git error: %s", e.stderr)
        return False
    except Exception as e:
        logger.error("Unexpected error rebasing branch: %s", e)
        return False
