import os
import subprocess

from codomyrmex.logging_monitoring import get_logger

_GIT_TIMEOUT = 60  # seconds

logger = get_logger(__name__)


def create_branch(branch_name: str, repository_path: str | None = None) -> bool:
    """Create and switch to a new Git branch."""
    if repository_path is None:
        repository_path = os.getcwd()

    try:
        subprocess.run(
            ["git", "checkout", "-b", branch_name],
            cwd=repository_path,
            capture_output=True,
            text=True,
            check=True,
            timeout=_GIT_TIMEOUT,
        )
        logger.debug("Branch '%s' created and checked out", branch_name)
        return True
    except subprocess.CalledProcessError as e:
        logger.error("Failed to create branch '%s': %s", branch_name, e.stderr or e)
        return False
    except Exception as e:
        logger.error("Unexpected error creating branch '%s': %s", branch_name, e)
        return False


def switch_branch(branch_name: str, repository_path: str | None = None) -> bool:
    """Switch to an existing Git branch."""
    if repository_path is None:
        repository_path = os.getcwd()

    try:
        subprocess.run(
            ["git", "checkout", branch_name],
            cwd=repository_path,
            capture_output=True,
            text=True,
            check=True,
            timeout=_GIT_TIMEOUT,
        )
        logger.debug("Switched to branch '%s'", branch_name)
        return True
    except subprocess.CalledProcessError as e:
        logger.error("Failed to switch to branch '%s': %s", branch_name, e.stderr or e)
        return False
    except Exception as e:
        logger.error("Unexpected error switching to branch '%s': %s", branch_name, e)
        return False


def delete_branch(
    branch_name: str, repository_path: str | None = None, force: bool = False
) -> bool:
    """Delete a local git branch.

    Args:
        branch_name: Name of the branch to delete.
        repository_path: Path to git repository (defaults to cwd).
        force: If True, use -D (force delete even if unmerged). Default False uses -d.
    """
    if repository_path is None:
        repository_path = os.getcwd()

    try:
        flag = "-D" if force else "-d"
        subprocess.run(
            ["git", "branch", flag, branch_name],
            cwd=repository_path,
            capture_output=True,
            text=True,
            check=True,
            timeout=_GIT_TIMEOUT,
        )
        logger.info("Deleted branch %s (force=%s)", branch_name, force)
        return True
    except subprocess.CalledProcessError as e:
        logger.error("Failed to delete branch '%s': %s", branch_name, e.stderr or e)
        return False
    except Exception as e:
        logger.error("Unexpected error deleting branch '%s': %s", branch_name, e)
        return False


def get_current_branch(repository_path: str | None = None) -> str:
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
            timeout=_GIT_TIMEOUT,
        )
        branch_name = result.stdout.strip()
        logger.debug("Current branch: %s", branch_name)
        return branch_name
    except (subprocess.CalledProcessError, Exception) as e:
        logger.error("Failed to get current branch: %s", e)
        return ""


def list_branches(repository_path: str | None = None) -> list[str]:
    """List all local branches in the repository.

    Args:
        repository_path: Path to the git repository. Defaults to current directory.

    Returns:
        List of branch names (current branch has no special marker).
        Returns empty list if not a git repository or on error.
    """
    cwd = repository_path or "."
    result = subprocess.run(
        ["git", "branch", "--list"],
        capture_output=True,
        text=True,
        cwd=cwd,
        check=True,
        timeout=_GIT_TIMEOUT,
    )
    branches = []
    for line in result.stdout.splitlines():
        name = line.lstrip("* ").strip()
        if name:
            branches.append(name)
    return branches
