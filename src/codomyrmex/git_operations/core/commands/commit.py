import os
import subprocess

from codomyrmex.logging_monitoring import get_logger
from codomyrmex.model_context_protocol.decorators import mcp_tool

from .status import add_files

_GIT_TIMEOUT = 60  # seconds

logger = get_logger(__name__)


def _git_config_value(key: str, repository_path: str) -> str:
    """Return a git config value or empty string if unset."""
    result = subprocess.run(
        ["git", "config", key],
        cwd=repository_path,
        capture_output=True,
        text=True,
        check=False,
        timeout=_GIT_TIMEOUT,
    )
    return result.stdout.strip() if result.returncode == 0 else ""


def _build_author_arg(
    author_name: str | None,
    author_email: str | None,
    repository_path: str,
) -> list[str]:
    """Build the --author git flag list from name/email overrides."""
    if author_name and author_email:
        return ["--author", f"{author_name} <{author_email}>"]
    if author_name:
        email = _git_config_value("user.email", repository_path)
        return (
            ["--author", f"{author_name} <{email}>"]
            if email
            else ["--author", author_name]
        )
    if author_email:
        name = _git_config_value("user.name", repository_path) or "Unknown"
        return ["--author", f"{name} <{author_email}>"]
    return []


def _stage_files_for_commit(
    file_paths: list[str] | None,
    stage_all: bool,
    repository_path: str,
) -> bool:
    """Stage files before committing. Returns False if staging failed."""
    if file_paths:
        if not add_files(file_paths, repository_path):
            logger.error("Failed to stage files for commit")
            return False
    elif stage_all:
        subprocess.run(
            ["git", "add", "-u"],
            cwd=repository_path,
            capture_output=True,
            text=True,
            check=True,
            timeout=_GIT_TIMEOUT,
        )
        logger.debug("Staged all tracked, modified files")
    return True


def _get_head_sha(repository_path: str) -> str:
    """Return the full SHA of HEAD."""
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=repository_path,
        capture_output=True,
        text=True,
        check=True,
        timeout=_GIT_TIMEOUT,
    )
    return result.stdout.strip()


@mcp_tool(name="git_commit")
def commit_changes(
    message: str,
    repository_path: str | None = None,
    author_name: str | None = None,
    author_email: str | None = None,
    stage_all: bool = True,
    file_paths: list[str] | None = None,
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
        logger.info("Committing changes with message: %s", message)
        if not _stage_files_for_commit(file_paths, stage_all, repository_path):
            return None
        cmd = [
            "git",
            "commit",
            *_build_author_arg(author_name, author_email, repository_path),
        ]
        cmd.extend(["-m", message])
        subprocess.run(
            cmd,
            cwd=repository_path,
            capture_output=True,
            text=True,
            check=True,
            timeout=_GIT_TIMEOUT,
        )
        commit_sha = _get_head_sha(repository_path)
        logger.info("Changes committed successfully: %s", commit_sha[:8])
        return commit_sha
    except subprocess.CalledProcessError as e:
        logger.error("Failed to commit changes: %s", e)
        if e.stderr:
            logger.error("Git error: %s", e.stderr)
        return None
    except Exception as e:
        logger.error("Unexpected error committing changes: %s", e)
        return None


@mcp_tool(name="git_revert")
def revert_commit(commit_sha: str, repository_path: str | None = None) -> bool:
    """Revert a specific commit by creating a new inverse commit."""
    if repository_path is None:
        repository_path = os.getcwd()
    try:
        logger.info("Reverting commit '%s' in %s", commit_sha, repository_path)
        subprocess.run(
            ["git", "revert", "--no-edit", commit_sha],
            cwd=repository_path,
            capture_output=True,
            text=True,
            check=True,
            timeout=_GIT_TIMEOUT,
        )
        logger.info("Successfully reverted commit %s", commit_sha[:8])
        return True
    except subprocess.CalledProcessError as e:
        logger.error("Failed to revert commit '%s': %s", commit_sha, e)
        if e.stderr:
            logger.error("Git error: %s", e.stderr)
        return False
    except Exception as e:
        logger.error("Unexpected error reverting commit: %s", e)
        return False


@mcp_tool(name="git_cherry_pick")
def cherry_pick(
    commit_sha: str, repository_path: str | None = None, no_commit: bool = False
) -> bool:
    """Cherry-pick a commit from another branch."""
    if repository_path is None:
        repository_path = os.getcwd()
    try:
        logger.info("Cherry-picking commit: %s", commit_sha)
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
            timeout=_GIT_TIMEOUT,
        )
        logger.info("Successfully cherry-picked commit %s", commit_sha[:8])
        return True
    except subprocess.CalledProcessError as e:
        logger.error("Failed to cherry-pick commit '%s': %s", commit_sha, e)
        if e.stderr:
            logger.error("Git error: %s", e.stderr)
        return False
    except Exception as e:
        logger.error("Unexpected error cherry-picking commit: %s", e)
        return False


@mcp_tool(name="git_amend")
def amend_commit(
    message: str | None = None,
    repository_path: str | None = None,
    author_name: str | None = None,
    author_email: str | None = None,
    no_edit: bool = False,
) -> str | None:
    """Amend the last commit."""
    if repository_path is None:
        repository_path = os.getcwd()
    try:
        logger.info("Amending last commit")
        cmd = ["git", "commit", "--amend"]
        if no_edit:
            cmd.extend(["-m", message] if message else ["--no-edit"])
        elif message:
            cmd.extend(["-m", message])
        else:
            cmd.append("--no-edit")
        cmd.extend(_build_author_arg(author_name, author_email, repository_path))
        subprocess.run(
            cmd,
            cwd=repository_path,
            capture_output=True,
            text=True,
            check=True,
            timeout=_GIT_TIMEOUT,
        )
        commit_sha = _get_head_sha(repository_path)
        logger.info("Successfully amended commit: %s", commit_sha[:8])
        return commit_sha
    except subprocess.CalledProcessError as e:
        logger.error("Failed to amend commit: %s", e)
        if e.stderr:
            logger.error("Git error: %s", e.stderr)
        return None
    except Exception as e:
        logger.error("Unexpected error amending commit: %s", e)
        return None
