import os
import subprocess

from codomyrmex.logging_monitoring.core.logger_config import get_logger
from codomyrmex.model_context_protocol.decorators import mcp_tool

logger = get_logger(__name__)

def add_files(file_paths: list[str], repository_path: str = None) -> bool:
    """Add files to the Git staging area."""
    if repository_path is None:
        repository_path = os.getcwd()

    try:
        logger.info(f"Adding files to staging area: {file_paths}")

        cmd = ["git", "add"] + file_paths
        subprocess.run(
            cmd, cwd=repository_path, capture_output=True, text=True, check=True
        )

        logger.info("Files added to staging area successfully")
        return True

    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to add files to staging area: {e}")
        if e.stderr:
            logger.error(f"Git error: {e.stderr}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error adding files: {e}")
        return False

@mcp_tool()
def get_status(repository_path: str = None) -> dict[str, any]:
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

        logger.debug(f"Repository status: {len(status_lines)} changes")
        return status_info

    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to get repository status: {e}")
        return {"error": str(e)}
    except Exception as e:
        logger.error(f"Unexpected error getting status: {e}")
        return {"error": str(e)}

def clean_repository(force: bool = False, directories: bool = False, repository_path: str = None) -> bool:
    """Clean untracked files from the repository."""
    if repository_path is None:
        repository_path = os.getcwd()

    try:
        cmd = ["git", "clean", "-f"]
        if force:
            cmd.append("-x") # Remove ignored files too if force is very true, typically just -f is enough for tracked, but here force param usually implies -f. Actually git clean requires -f.
            # Let's interpret 'force' as -x (ignored files) and always use -f.
            pass

        # Actually, standard git clean usage:
        # -f is required via configuration or flag.
        # -d for directories.
        # -x for ignored files.

        base_cmd = ["git", "clean", "-f"] # Force is required by default in most extensive configs
        if directories:
            base_cmd.append("-d")
        if force:
            base_cmd.append("-x")

        logger.info(f"Cleaning repository in {repository_path}")
        subprocess.run(
            base_cmd,
            cwd=repository_path,
            capture_output=True,
            text=True,
            check=True,
        )
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to clean repository: {e}")
        return False

def get_diff(target: str = "HEAD", repository_path: str = None, cached: bool = False) -> str:
    """Get the diff of current changes against a target."""
    if repository_path is None:
        repository_path = os.getcwd()

    try:
        cmd = ["git", "diff"]
        if cached:
            cmd.append("--cached")
        cmd.append(target)

        result = subprocess.run(
            cmd,
            cwd=repository_path,
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to get diff: {e}")
        return ""
    except FileNotFoundError:
        return ""
    except Exception as e:
        logger.error(f"Unexpected error getting diff: {e}")
        return ""

def get_diff_files(
    file_path: str = None, staged: bool = False, repository_path: str = None
) -> str:
    """Get diff of changes."""
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
            cmd, cwd=repository_path, capture_output=True, text=True, check=True
        )

        logger.debug(f"Retrieved diff ({len(result.stdout)} characters)")
        return result.stdout

    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to get diff: {e}")
        return ""
    except Exception as e:
        logger.error(f"Unexpected error getting diff: {e}")
        return ""

def reset_changes(
    mode: str = "mixed", target: str = "HEAD", repository_path: str = None
) -> bool:
    """Reset repository to a specific state."""
    if repository_path is None:
        repository_path = os.getcwd()

    valid_modes = ["soft", "mixed", "hard"]
    if mode not in valid_modes:
        logger.error(f"Invalid reset mode '{mode}'. Valid modes: {valid_modes}")
        return False

    try:
        logger.info(
            f"Resetting repository to '{target}' with mode '{mode}' in {repository_path}"
        )

        cmd = ["git", "reset", f"--{mode}", target]
        subprocess.run(
            cmd, cwd=repository_path, capture_output=True, text=True, check=True
        )

        logger.info("Repository reset successfully")
        return True

    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to reset repository: {e}")
        if e.stderr:
            logger.error(f"Git error: {e.stderr}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error resetting repository: {e}")
        return False

