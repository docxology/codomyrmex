import os
import subprocess

from codomyrmex.logging_monitoring.core.logger_config import get_logger
from codomyrmex.model_context_protocol.decorators import mcp_tool

logger = get_logger(__name__)

@mcp_tool()
def create_branch(branch_name: str, repository_path: str = None) -> bool:
    """Create and switch to a new Git branch."""
    if repository_path is None:
        repository_path = os.getcwd()

    try:
        logger.info(f"Creating new branch '{branch_name}' in {repository_path}")

        # Create and switch to new branch
        subprocess.run(
            ["git", "checkout", "-b", branch_name],
            cwd=repository_path,
            capture_output=True,
            text=True,
            check=True,
        )

        logger.info(f"Branch '{branch_name}' created and checked out successfully")
        return True

    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to create branch '{branch_name}': {e}")
        if e.stderr:
            logger.error(f"Git error: {e.stderr}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error creating branch: {e}")
        return False

@mcp_tool()
def switch_branch(branch_name: str, repository_path: str = None) -> bool:
    """Switch to an existing Git branch."""
    if repository_path is None:
        repository_path = os.getcwd()

    try:
        logger.info(f"Switching to branch '{branch_name}' in {repository_path}")

        subprocess.run(
            ["git", "checkout", branch_name],
            cwd=repository_path,
            capture_output=True,
            text=True,
            check=True,
        )

        logger.info(f"Switched to branch '{branch_name}' successfully")
        return True

    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to switch to branch '{branch_name}': {e}")
        if e.stderr:
            logger.error(f"Git error: {e.stderr}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error switching branch: {e}")
        return False

def delete_branch(branch_name: str, repository_path: str = None, force: bool = False) -> bool:
    """Delete a local git branch.

    Args:
        branch_name: Name of the branch to delete.
        repository_path: Path to git repository (defaults to cwd).
        force: If True, use -D (force delete even if unmerged). Default False uses -d.
    """
    if repository_path is None:
        repository_path = os.getcwd()

    flag = "-D" if force else "-d"
    result = subprocess.run(
        ["git", "branch", flag, branch_name],
        capture_output=True, text=True, cwd=repository_path
    )
    if result.returncode != 0:
        logger.error("Failed to delete branch %s: %s", branch_name, result.stderr.strip())
        return False
    logger.info("Deleted branch %s (force=%s)", branch_name, force)
    return True

@mcp_tool()
def get_current_branch(repository_path: str = None) -> str | None:
    """Get the name of the current Git branch."""
    if repository_path is None:
        repository_path = os.getcwd()

    try:
        result = subprocess.run(
            ["git", "branch", "--show-current"],
            cwd=repository_path,
            capture_output=True,
            text=True,
            check=True,
        )

        branch_name = result.stdout.strip()
        logger.debug(f"Current branch: {branch_name}")
        return branch_name

    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to get current branch: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error getting current branch: {e}")
        return None

