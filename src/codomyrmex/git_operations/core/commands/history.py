import os
import subprocess

from codomyrmex.logging_monitoring.core.logger_config import get_logger
from codomyrmex.model_context_protocol.decorators import mcp_tool

logger = get_logger(__name__)

@mcp_tool()
def get_commit_history(
    limit: int = 10, repository_path: str = None
) -> list[dict[str, str]]:
    """Get recent commit history."""
    if repository_path is None:
        repository_path = os.getcwd()

    try:
        logger.debug(f"Getting commit history (limit: {limit})")

        result = subprocess.run(
            [
                "git",
                "log",
                "--oneline",
                "-n",
                str(limit),
                "--pretty=format:%H|%an|%ae|%ad|%s",
            ],
            cwd=repository_path,
            capture_output=True,
            text=True,
            check=True,
        )

        commits = []
        for line in result.stdout.strip().split("\n"):
            if line.strip():
                parts = line.split("|", 4)
                if len(parts) == 5:
                    commits.append(
                        {
                            "hash": parts[0],
                            "author_name": parts[1],
                            "author_email": parts[2],
                            "date": parts[3],
                            "message": parts[4],
                        }
                    )

        logger.debug(f"Retrieved {len(commits)} commits")
        return commits

    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to get commit history: {e}")
        return []
    except Exception as e:
        logger.error(f"Unexpected error getting commit history: {e}")
        return []

def get_blame(file_path: str, repository_path: str = None) -> str:
    """Get the blame for a file."""
    if repository_path is None:
        repository_path = os.getcwd()

    try:
        result = subprocess.run(
            ["git", "blame", file_path],
            cwd=repository_path,
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to get blame for {file_path}: {e}")
        return ""

def get_commit_details(commit_sha: str, repository_path: str = None) -> dict:
    """Get detailed information about a specific commit."""
    if repository_path is None:
        repository_path = os.getcwd()

    try:
        # format: hash|author|email|date|subject|body
        fmt = "%H|%an|%ae|%ad|%s|%b"
        result = subprocess.run(
            ["git", "show", "-s", f"--format={fmt}", commit_sha],
            cwd=repository_path,
            capture_output=True,
            text=True,
            check=True,
        )

        parts = result.stdout.strip().split("|", 5)
        if len(parts) < 6:
            return {}

        return {
            "hash": parts[0],
            "author": parts[1],
            "email": parts[2],
            "date": parts[3],
            "subject": parts[4],
            "body": parts[5]
        }
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to get commit details for {commit_sha}: {e}")
        return {}

def get_commit_history_filtered(
    limit: int = 10,
    repository_path: str = None,
    since: str = None,
    until: str = None,
    author: str = None,
    branch: str = None,
    file_path: str = None,
) -> list[dict[str, str]]:
    """
    Get commit history with filters.

    Args:
        limit: Maximum number of commits to return
        repository_path: Path to repository
        since: Show commits after this date (ISO format or relative like "2 weeks ago")
        until: Show commits before this date (ISO format or relative)
        author: Filter by author name or email
        branch: Branch to show commits from
        file_path: Show only commits affecting this file

    Returns:
        List of commit dictionaries
    """
    if repository_path is None:
        repository_path = os.getcwd()

    try:
        logger.debug(f"Getting filtered commit history (limit: {limit})")

        cmd = [
            "git",
            "log",
            "--oneline",
            "-n",
            str(limit),
            "--pretty=format:%H|%an|%ae|%ad|%s",
        ]

        if since:
            cmd.extend(["--since", since])
        if until:
            cmd.extend(["--until", until])
        if author:
            cmd.extend(["--author", author])
        if file_path:
            cmd.append("--")
            cmd.append(file_path)

        if branch:
            cmd.append(branch)

        result = subprocess.run(
            cmd,
            cwd=repository_path,
            capture_output=True,
            text=True,
            check=True,
        )

        commits = []
        for line in result.stdout.strip().split("\n"):
            if line.strip():
                parts = line.split("|", 4)
                if len(parts) == 5:
                    commits.append(
                        {
                            "hash": parts[0],
                            "author_name": parts[1],
                            "author_email": parts[2],
                            "date": parts[3],
                            "message": parts[4],
                        }
                    )

        logger.debug(f"Retrieved {len(commits)} filtered commits")
        return commits

    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to get filtered commit history: {e}")
        return []
    except Exception as e:
        logger.error(f"Unexpected error getting filtered commit history: {e}")
        return []

