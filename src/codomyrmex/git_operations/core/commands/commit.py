import os
import subprocess

from codomyrmex.logging_monitoring.core.logger_config import get_logger
from codomyrmex.model_context_protocol.decorators import mcp_tool

from .status import add_files

logger = get_logger(__name__)

@mcp_tool()
def commit_changes(
    message: str,
    repository_path: str = None,
    author_name: str = None,
    author_email: str = None,
    stage_all: bool = True,
    file_paths: list[str] = None,
) -> str | None:
    """
    Commit staged changes with the given message.

    Args:
        message: Commit message
        repository_path: Path to repository (defaults to current directory)
        author_name: Override Git config for author name
        author_email: Override Git config for author email
        stage_all: If True, stages all tracked, modified files before committing (default: True)
        file_paths: Optional list of specific files to stage and commit (if provided, stage_all is ignored)

    Returns:
        SHA of the new commit on success, None on failure
    """
    if repository_path is None:
        repository_path = os.getcwd()

    try:
        logger.info(f"Committing changes with message: {message}")

        # Stage files if needed
        if file_paths:
            # Stage specific files
            if not add_files(file_paths, repository_path):
                logger.error("Failed to stage files for commit")
                return None
        elif stage_all:
            # Stage all tracked, modified files
            subprocess.run(
                ["git", "add", "-u"],
                cwd=repository_path,
                capture_output=True,
                text=True,
                check=True,
            )
            logger.debug("Staged all tracked, modified files")

        # Build commit command
        cmd = ["git", "commit"]

        # Add author override if provided
        if author_name and author_email:
            cmd.extend(["--author", f"{author_name} <{author_email}>"])
        elif author_name:
            # If only name provided, try to get email from config or use name only
            email_result = subprocess.run(
                ["git", "config", "user.email"],
                cwd=repository_path,
                capture_output=True,
                text=True,
                check=False,
            )
            email = email_result.stdout.strip() if email_result.returncode == 0 else ""
            if email:
                cmd.extend(["--author", f"{author_name} <{email}>"])
            else:
                cmd.extend(["--author", author_name])
        elif author_email:
            # If only email provided, try to get name from config
            name_result = subprocess.run(
                ["git", "config", "user.name"],
                cwd=repository_path,
                capture_output=True,
                text=True,
                check=False,
            )
            name = name_result.stdout.strip() if name_result.returncode == 0 else "Unknown"
            cmd.extend(["--author", f"{name} <{author_email}>"])

        # Add commit message
        cmd.extend(["-m", message])

        # Execute commit
        subprocess.run(
            cmd,
            cwd=repository_path,
            capture_output=True,
            text=True,
            check=True,
        )

        # Get commit SHA
        sha_result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=repository_path,
            capture_output=True,
            text=True,
            check=True,
        )

        commit_sha = sha_result.stdout.strip()
        logger.info(f"Changes committed successfully: {commit_sha[:8]}")
        return commit_sha

    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to commit changes: {e}")
        if e.stderr:
            logger.error(f"Git error: {e.stderr}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error committing changes: {e}")
        return None

def revert_commit(commit_sha: str, repository_path: str = None) -> bool:
    """Revert a specific commit."""
    if repository_path is None:
        repository_path = os.getcwd()

    try:
        logger.info(f"Reverting commit '{commit_sha}' in {repository_path}")
        # --no-edit to avoid opening editor for commit message
        subprocess.run(
            ["git", "revert", "--no-edit", commit_sha],
            cwd=repository_path,
            capture_output=True,
            text=True,
            check=True,
        )
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to revert commit '{commit_sha}': {e}")
        return False

def cherry_pick(
    commit_sha: str, repository_path: str = None, no_commit: bool = False
) -> bool:
    """Cherry-pick a commit from another branch."""
    if repository_path is None:
        repository_path = os.getcwd()

    try:
        logger.info(f"Cherry-picking commit: {commit_sha}")

        cmd = ["git", "cherry-pick"]
        if no_commit:
            cmd.append("--no-commit")
        cmd.append(commit_sha)

        subprocess.run(
            cmd,
            cwd=repository_path,
            capture_output=True,
            text=True,
            check=True,
        )

        logger.info(f"Successfully cherry-picked commit {commit_sha[:8]}")
        return True

    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to cherry-pick commit '{commit_sha}': {e}")
        if e.stderr:
            logger.error(f"Git error: {e.stderr}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error cherry-picking commit: {e}")
        return False

def amend_commit(
    message: str = None,
    repository_path: str = None,
    author_name: str = None,
    author_email: str = None,
    no_edit: bool = False,
) -> str | None:
    """Amend the last commit."""
    if repository_path is None:
        repository_path = os.getcwd()

    try:
        logger.info("Amending last commit")

        cmd = ["git", "commit", "--amend"]

        if no_edit:
            if message:
                cmd.extend(["-m", message])
            else:
                cmd.append("--no-edit")
        elif message:
            cmd.extend(["-m", message])
        else:
            cmd.append("--no-edit")

        # Add author override if provided
        if author_name and author_email:
            cmd.extend(["--author", f"{author_name} <{author_email}>"])
        elif author_name:
            email_result = subprocess.run(
                ["git", "config", "user.email"],
                cwd=repository_path,
                capture_output=True,
                text=True,
                check=False,
            )
            email = email_result.stdout.strip() if email_result.returncode == 0 else ""
            if email:
                cmd.extend(["--author", f"{author_name} <{email}>"])
            else:
                cmd.extend(["--author", author_name])
        elif author_email:
            name_result = subprocess.run(
                ["git", "config", "user.name"],
                cwd=repository_path,
                capture_output=True,
                text=True,
                check=False,
            )
            name = name_result.stdout.strip() if name_result.returncode == 0 else "Unknown"
            cmd.extend(["--author", f"{name} <{author_email}>"])

        subprocess.run(
            cmd,
            cwd=repository_path,
            capture_output=True,
            text=True,
            check=True,
        )

        # Get amended commit SHA
        sha_result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=repository_path,
            capture_output=True,
            text=True,
            check=True,
        )

        commit_sha = sha_result.stdout.strip()
        logger.info(f"Successfully amended commit: {commit_sha[:8]}")
        return commit_sha

    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to amend commit: {e}")
        if e.stderr:
            logger.error(f"Git error: {e.stderr}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error amending commit: {e}")
        return None

