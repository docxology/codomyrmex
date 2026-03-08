import os
import subprocess
from typing import Any

from codomyrmex.logging_monitoring import get_logger
from codomyrmex.model_context_protocol.decorators import mcp_tool

_GIT_TIMEOUT = 60  # seconds

logger = get_logger(__name__)


@mcp_tool(name="git_add")
def add_files(file_paths: list[str], repository_path: str | None = None) -> bool:
    """Add files to the Git staging area."""
    if repository_path is None:
        repository_path = os.getcwd()

    if not file_paths:
        logger.warning("No files specified to add")
        return True

    try:
        logger.info("Adding files to staging area: %s", file_paths)

        cmd = ["git", "add", *file_paths]
        subprocess.run(
            cmd,
            cwd=repository_path,
            capture_output=True,
            text=True,
            check=True,
            timeout=_GIT_TIMEOUT,
        )

        logger.info("Files added to staging area successfully")
        return True

    except subprocess.CalledProcessError as e:
        logger.error("Failed to add files to staging area: %s", e)
        if e.stderr:
            logger.error("Git error: %s", e.stderr)
        return False
    except Exception as e:
        logger.error("Unexpected error adding files: %s", e)
        return False


@mcp_tool(name="git_repo_status")
def get_status(repository_path: str | None = None) -> dict[str, Any]:
    """Get the current Git repository status."""
    if repository_path is None:
        repository_path = os.getcwd()

    try:
        logger.debug("Getting Git repository status")

        result = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=repository_path,
            capture_output=True,
            text=True,
            check=True,
            timeout=_GIT_TIMEOUT,
        )

        status_lines = (
            result.stdout.strip().split("\n") if result.stdout.strip() else []
        )

        status_info = {
            "modified": [],
            "added": [],
            "deleted": [],
            "renamed": [],
            "untracked": [],
            "clean": len(status_lines) == 0,
        }

        for line in status_lines:
            if not line.strip():
                continue

            # Git status --porcelain format: XY filename
            # X = index status, Y = worktree status
            if len(line) < 3:
                continue

            index_status = line[0]
            worktree_status = line[1]
            filename = line[3:]  # Skip the space after status codes

            # Check index status (staged changes)
            if index_status == "A":
                status_info["added"].append(filename)
            elif index_status == "M":
                status_info["modified"].append(filename)
            elif index_status == "D":
                status_info["deleted"].append(filename)
            elif index_status == "R":
                status_info["renamed"].append(filename)

            # Check worktree status (unstaged changes)
            if worktree_status == "M":
                if filename not in status_info["modified"]:
                    status_info["modified"].append(filename)
            elif worktree_status == "D":
                if filename not in status_info["deleted"]:
                    status_info["deleted"].append(filename)

            # Untracked files
            if index_status == "?" and worktree_status == "?":
                status_info["untracked"].append(filename)

        logger.debug("Repository status: %s changes", len(status_lines))
        return status_info

    except subprocess.CalledProcessError as e:
        logger.error("Failed to get repository status: %s", e)
        return {"error": str(e)}
    except Exception as e:
        logger.error("Unexpected error getting status: %s", e)
        return {"error": str(e)}


@mcp_tool(name="git_clean")
def clean_repository(
    force: bool = False, directories: bool = False, repository_path: str | None = None
) -> bool:
    """Clean untracked files from the repository."""
    if repository_path is None:
        repository_path = os.getcwd()

    try:
        # -f is required to actually delete things unless clean.requireForce is set to false
        base_cmd = ["git", "clean", "-f"]
        if directories:
            base_cmd.append("-d")
        if force:
            # -x also removes ignored files
            base_cmd.append("-x")

        logger.info("Cleaning repository in %s", repository_path)
        subprocess.run(
            base_cmd,
            cwd=repository_path,
            capture_output=True,
            text=True,
            check=True,
            timeout=_GIT_TIMEOUT,
        )
        return True
    except subprocess.CalledProcessError as e:
        logger.error("Failed to clean repository: %s", e)
        if e.stderr:
            logger.error("Git error: %s", e.stderr)
        return False
    except Exception as e:
        logger.error("Unexpected error cleaning repository: %s", e)
        return False


@mcp_tool(name="git_diff")
def get_diff(
    target: str | None = None, repository_path: str | None = None, cached: bool = False
) -> str:
    """Get the diff of current changes.

    Args:
        target: Optional target to diff against (e.g. 'HEAD', 'main', or a commit SHA).
                If None and cached=False, diffs working tree against index.
                If None and cached=True, diffs index against HEAD.
        repository_path: Path to repository.
        cached: If True, show staged changes (equivalent to --cached/--staged).
    """
    if repository_path is None:
        repository_path = os.getcwd()

    try:
        cmd = ["git", "diff"]
        if cached:
            cmd.append("--cached")
        if target:
            cmd.append(target)

        result = subprocess.run(
            cmd,
            cwd=repository_path,
            capture_output=True,
            text=True,
            check=True,
            timeout=_GIT_TIMEOUT,
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        logger.error("Failed to get diff: %s", e)
        return ""
    except FileNotFoundError as e:
        logger.warning("Git not found when getting diff: %s", e)
        return ""
    except Exception as e:
        logger.error("Unexpected error getting diff: %s", e)
        return ""


@mcp_tool(name="git_diff_files")
def get_diff_files(
    file_path: str | None = None,
    staged: bool = False,
    repository_path: str | None = None,
) -> str:
    """Get diff of changes for a specific file or all files."""
    if repository_path is None:
        repository_path = os.getcwd()

    try:
        logger.debug("Getting Git diff")

        cmd = ["git", "diff"]
        if staged:
            cmd.append("--staged")
        if file_path:
            cmd.append(file_path)

        result = subprocess.run(
            cmd,
            cwd=repository_path,
            capture_output=True,
            text=True,
            check=True,
            timeout=_GIT_TIMEOUT,
        )

        logger.debug("Retrieved diff (%s characters)", len(result.stdout))
        return result.stdout

    except subprocess.CalledProcessError as e:
        logger.error("Failed to get diff: %s", e)
        return ""
    except Exception as e:
        logger.error("Unexpected error getting diff: %s", e)
        return ""


@mcp_tool(name="git_reset")
def reset_changes(
    mode: str = "mixed", target: str = "HEAD", repository_path: str | None = None
) -> bool:
    """Reset repository to a specific state."""
    if repository_path is None:
        repository_path = os.getcwd()

    valid_modes = ["soft", "mixed", "hard"]
    if mode not in valid_modes:
        logger.error("Invalid reset mode '%s'. Valid modes: %s", mode, valid_modes)
        return False

    try:
        logger.info(
            f"Resetting repository to '{target}' with mode '{mode}' in {repository_path}"
        )

        cmd = ["git", "reset", f"--{mode}", target]
        subprocess.run(
            cmd,
            cwd=repository_path,
            capture_output=True,
            text=True,
            check=True,
            timeout=_GIT_TIMEOUT,
        )

        logger.info("Repository reset successfully")
        return True

    except subprocess.CalledProcessError as e:
        logger.error("Failed to reset repository: %s", e)
        if e.stderr:
            logger.error("Git error: %s", e.stderr)
        return False
    except Exception as e:
        logger.error("Unexpected error resetting repository: %s", e)
        return False
