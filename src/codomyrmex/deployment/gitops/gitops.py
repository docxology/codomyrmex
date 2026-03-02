"""GitOps synchronization utilities."""

import logging
import os
import subprocess

logger = logging.getLogger(__name__)

class GitOpsSynchronizer:
    """Synchronizes target state from a Git repository."""

    def __init__(self, repo_url: str, local_path: str):
        """Initialize this instance."""
        self.repo_url = repo_url
        self.local_path = local_path

    def sync(self, branch: str = "main") -> bool:
        """Clone or pull the repository to ensure local path is current."""
        try:
            if not os.path.exists(self.local_path):
                logger.info(f"Cloning {self.repo_url} to {self.local_path}")
                subprocess.run(["git", "clone", "-b", branch, self.repo_url, self.local_path], check=True)
            else:
                logger.info(f"Updating {self.local_path} from {self.repo_url}")
                # Ensure we are in the right directory and branch
                subprocess.run(["git", "-C", self.local_path, "fetch", "origin"], check=True)
                subprocess.run(["git", "-C", self.local_path, "reset", "--hard", f"origin/{branch}"], check=True)
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"GitOps sync failed: {e}")
            return False

    def get_version(self) -> str | None:
        """Get the current commit SHA of the synchronized repo."""
        try:
            result = subprocess.run(
                ["git", "-C", self.local_path, "rev-parse", "HEAD"],
                capture_output=True, text=True, check=True
            )
            return result.stdout.strip()
        except Exception as e:
            logger.warning("Failed to get repo version at %s: %s", self.local_path, e)
            return None
