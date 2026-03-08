import os
import subprocess

from codomyrmex.logging_monitoring import get_logger
from codomyrmex.model_context_protocol.decorators import mcp_tool

_GIT_TIMEOUT = 120  # seconds

logger = get_logger(__name__)


@mcp_tool(name="git_fetch")
def fetch_remote(remote: str = "origin", repository_path: str | None = None) -> bool:
    """Fetch changes from a remote."""
    if repository_path is None:
        repository_path = os.getcwd()

    try:
        logger.info("Fetching from remote '%s' in %s", remote, repository_path)
        subprocess.run(
            ["git", "fetch", remote],
            cwd=repository_path,
            capture_output=True,
            text=True,
            check=True,
            timeout=_GIT_TIMEOUT,
        )
        return True
    except subprocess.CalledProcessError as e:
        logger.error("Failed to fetch remote '%s': %s", remote, e)
        if e.stderr:
            logger.error("Git error: %s", e.stderr)
        raise
    except Exception as e:
        logger.error("Unexpected error fetching remote: %s", e)
        raise


@mcp_tool(name="git_prune_remote")
def prune_remote(remote: str = "origin", repository_path: str | None = None) -> bool:
    """Prune remote tracking branches."""
    if repository_path is None:
        repository_path = os.getcwd()

    try:
        logger.info("Pruning remote '%s' in %s", remote, repository_path)
        subprocess.run(
            ["git", "remote", "prune", remote],
            cwd=repository_path,
            capture_output=True,
            text=True,
            check=True,
            timeout=_GIT_TIMEOUT,
        )
        return True
    except subprocess.CalledProcessError as e:
        logger.error("Failed to prune remote '%s': %s", remote, e)
        if e.stderr:
            logger.error("Git error: %s", e.stderr)
        raise
    except Exception as e:
        logger.error("Unexpected error pruning remote: %s", e)
        raise


@mcp_tool(name="git_add_remote")
def add_remote(remote_name: str, url: str, repository_path: str | None = None) -> bool:
    """Add a remote repository."""
    if repository_path is None:
        repository_path = os.getcwd()

    try:
        logger.info("Adding remote '%s' with URL: %s", remote_name, url)

        subprocess.run(
            ["git", "remote", "add", remote_name, url],
            cwd=repository_path,
            capture_output=True,
            text=True,
            check=True,
            timeout=_GIT_TIMEOUT,
        )

        logger.info("Remote '%s' added successfully", remote_name)
        return True

    except subprocess.CalledProcessError as e:
        logger.error("Failed to add remote '%s': %s", remote_name, e)
        if e.stderr:
            logger.error("Git error: %s", e.stderr)
        raise
    except Exception as e:
        logger.error("Unexpected error adding remote: %s", e)
        raise


@mcp_tool(name="git_remove_remote")
def remove_remote(remote_name: str, repository_path: str | None = None) -> bool:
    """Remove a remote repository."""
    if repository_path is None:
        repository_path = os.getcwd()

    try:
        logger.info("Removing remote '%s'", remote_name)

        subprocess.run(
            ["git", "remote", "remove", remote_name],
            cwd=repository_path,
            capture_output=True,
            text=True,
            check=True,
            timeout=_GIT_TIMEOUT,
        )

        logger.info("Remote '%s' removed successfully", remote_name)
        return True

    except subprocess.CalledProcessError as e:
        logger.error("Failed to remove remote '%s': %s", remote_name, e)
        if e.stderr:
            logger.error("Git error: %s", e.stderr)
        raise
    except Exception as e:
        logger.error("Unexpected error removing remote: %s", e)
        raise


@mcp_tool(name="git_list_remotes")
def list_remotes(repository_path: str | None = None) -> list[dict[str, str]]:
    """List all remote repositories."""
    if repository_path is None:
        repository_path = os.getcwd()

    try:
        logger.debug("Listing Git remotes")

        result = subprocess.run(
            ["git", "remote", "-v"],
            cwd=repository_path,
            capture_output=True,
            text=True,
            check=True,
            timeout=_GIT_TIMEOUT,
        )

        remotes = []
        seen_remotes = set()
        for line in result.stdout.strip().split("\n"):
            if line.strip():
                parts = line.split()
                if len(parts) >= 2:
                    name = parts[0]
                    url = parts[1]
                    fetch_or_push = parts[2] if len(parts) > 2 else "fetch"

                    if name not in seen_remotes:
                        remotes.append(
                            {
                                "name": name,
                                "url": url,
                                "fetch": url if fetch_or_push == "(fetch)" else None,
                                "push": url if fetch_or_push == "(push)" else None,
                            }
                        )
                        seen_remotes.add(name)
                    else:
                        # Update existing remote with push URL if needed
                        for remote in remotes:
                            if remote["name"] == name and fetch_or_push == "(push)":
                                remote["push"] = url

        logger.debug(f"Found {len(remotes)} remotes")
        return remotes

    except subprocess.CalledProcessError as e:
        logger.error("Failed to list remotes: %s", e)
        raise
    except Exception as e:
        logger.error("Unexpected error listing remotes: %s", e)
        raise
