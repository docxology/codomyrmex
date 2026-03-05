import os
import subprocess

from codomyrmex.logging_monitoring import get_logger
from codomyrmex.model_context_protocol.decorators import mcp_tool

from .branching import get_current_branch, switch_branch

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
            f"Merging branch '{source_branch}' into '{target_branch}' in {repository_path}"
        )

        # Switch to target branch first; CalledProcessError propagates to outer except
        switch_branch(target_branch, repository_path)

        # Prepare merge command
        cmd = ["git", "merge", "--no-edit"]
        if strategy:
            cmd.extend(["-s", strategy])
        cmd.append(source_branch)

        subprocess.run(
            cmd, cwd=repository_path, capture_output=True, text=True, check=True
        )

        logger.info(f"Successfully merged '{source_branch}' into '{target_branch}'")
        return True

    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to merge branch '{source_branch}': {e}")
        if e.stderr:
            logger.error(f"Git error: {e.stderr}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error merging branch: {e}")
        raise


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
            f"Rebasing branch '{current_branch}' onto '{target_branch}' in {repository_path}"
        )

        cmd = ["git", "rebase"]
        if interactive:
            cmd.append("-i")
        cmd.append(target_branch)

        subprocess.run(
            cmd, cwd=repository_path, capture_output=True, text=True, check=True
        )

        logger.info(f"Successfully rebased '{current_branch}' onto '{target_branch}'")
        return True

    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to rebase onto '{target_branch}': {e}")
        if e.stderr:
            logger.error(f"Git error: {e.stderr}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error rebasing branch: {e}")
        raise
