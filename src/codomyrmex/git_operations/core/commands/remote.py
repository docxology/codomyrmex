import os
import subprocess

from codomyrmex.logging_monitoring.core.logger_config import get_logger

logger = get_logger(__name__)

def fetch_remote(remote: str = "origin", repository_path: str = None) -> bool:
    """Fetch changes from a remote."""
    if repository_path is None:
        repository_path = os.getcwd()

    try:
        logger.info(f"Fetching from remote '{remote}' in {repository_path}")
        subprocess.run(
            ["git", "fetch", remote],
            cwd=repository_path,
            capture_output=True,
            text=True,
            check=True,
        )
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to fetch remote '{remote}': {e}")
        return False

def prune_remote(remote: str = "origin", repository_path: str = None) -> bool:
    """Prune remote tracking branches."""
    if repository_path is None:
        repository_path = os.getcwd()

    try:
        logger.info(f"Pruning remote '{remote}' in {repository_path}")
        subprocess.run(
            ["git", "remote", "prune", remote],
            cwd=repository_path,
            capture_output=True,
            text=True,
            check=True,
        )
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to prune remote '{remote}': {e}")
        return False

def add_remote(
    remote_name: str, url: str, repository_path: str = None
) -> bool:
    """Add a remote repository."""
    if repository_path is None:
        repository_path = os.getcwd()

    try:
        logger.info(f"Adding remote '{remote_name}' with URL: {url}")

        subprocess.run(
            ["git", "remote", "add", remote_name, url],
            cwd=repository_path,
            capture_output=True,
            text=True,
            check=True,
        )

        logger.info(f"Remote '{remote_name}' added successfully")
        return True

    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to add remote '{remote_name}': {e}")
        if e.stderr:
            logger.error(f"Git error: {e.stderr}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error adding remote: {e}")
        return False

def remove_remote(remote_name: str, repository_path: str = None) -> bool:
    """Remove a remote repository."""
    if repository_path is None:
        repository_path = os.getcwd()

    try:
        logger.info(f"Removing remote '{remote_name}'")

        subprocess.run(
            ["git", "remote", "remove", remote_name],
            cwd=repository_path,
            capture_output=True,
            text=True,
            check=True,
        )

        logger.info(f"Remote '{remote_name}' removed successfully")
        return True

    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to remove remote '{remote_name}': {e}")
        if e.stderr:
            logger.error(f"Git error: {e.stderr}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error removing remote: {e}")
        return False

def list_remotes(repository_path: str = None) -> list[dict[str, str]]:
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
                        remotes.append({
                            "name": name,
                            "url": url,
                            "fetch": url if fetch_or_push == "(fetch)" else None,
                            "push": url if fetch_or_push == "(push)" else None,
                        })
                        seen_remotes.add(name)
                    else:
                        # Update existing remote with push URL if needed
                        for remote in remotes:
                            if remote["name"] == name and fetch_or_push == "(push)":
                                remote["push"] = url

        logger.debug(f"Found {len(remotes)} remotes")
        return remotes

    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to list remotes: {e}")
        return []
    except Exception as e:
        logger.error(f"Unexpected error listing remotes: {e}")
        return []

