"""GitOps synchronization utilities."""

import os
import shutil
import subprocess

from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)


class GitOpsSynchronizer:
    """Synchronizes target state from a Git repository.

    Provides mechanisms to clone, fetch, and reset to specific branches or
    commits to ensure the local configuration matches the source of truth.
    """

    def __init__(self, repo_url: str, local_path: str):
        """Initialize the synchronizer.

        Args:
            repo_url: URL of the Git repository.
            local_path: Local directory path to synchronize with.
        """
        self.repo_url = repo_url
        self.local_path = local_path

    def sync(self, branch: str = "main") -> bool:
        """Clone or pull the repository to ensure local path is current.

        Args:
            branch: The Git branch to synchronize.

        Returns:
            True if synchronization was successful, False otherwise.
        """
        try:
            if not os.path.exists(self.local_path):
                logger.info("Cloning %s to %s", self.repo_url, self.local_path)
                res = subprocess.run(
                    ["git", "clone", "-b", branch, self.repo_url, self.local_path],
                    capture_output=True,
                    text=True,
                    timeout=60,
                )
                if res.returncode != 0:
                    logger.error("Git clone failed: %s", res.stderr)
                    return False
            else:
                logger.info("Updating %s from %s", self.local_path, self.repo_url)
                # Ensure we are in a Git repository
                if not os.path.exists(os.path.join(self.local_path, ".git")):
                    logger.warning(
                        "%s exists but is not a Git repo. Re-cloning.", self.local_path
                    )
                    shutil.rmtree(self.local_path)
                    return self.sync(branch)

                res = subprocess.run(
                    ["git", "-C", self.local_path, "fetch", "origin"],
                    capture_output=True,
                    text=True,
                    timeout=60,
                )
                if res.returncode != 0:
                    logger.error("Git fetch failed: %s", res.stderr)
                    return False

                res = subprocess.run(
                    [
                        "git",
                        "-C",
                        self.local_path,
                        "reset",
                        "--hard",
                        f"origin/{branch}",
                    ],
                    capture_output=True,
                    text=True,
                    timeout=60,
                )
                if res.returncode != 0:
                    logger.error("Git reset failed: %s", res.stderr)
                    return False
            return True
        except (subprocess.CalledProcessError, OSError) as e:
            logger.error("GitOps sync failed: %s", str(e))
            return False

    def get_version(self) -> str | None:
        """Get the current commit SHA of the synchronized repo.

        Returns:
            Current commit hash (long form), or None if the version
            cannot be determined.
        """
        try:
            if not os.path.exists(self.local_path) or not os.path.exists(
                os.path.join(self.local_path, ".git")
            ):
                return None

            result = subprocess.run(
                ["git", "-C", self.local_path, "rev-parse", "HEAD"],
                capture_output=True,
                text=True,
                check=True,
                timeout=10,
            )
            return result.stdout.strip()
        except (subprocess.CalledProcessError, OSError) as e:
            logger.warning("Failed to get repo version at %s: %s", self.local_path, e)
            return None

    def checkout(self, revision: str) -> bool:
        """Check out a specific revision (commit SHA, tag, or branch).

        Args:
            revision: The target revision to checkout.

        Returns:
            True if checkout was successful, False otherwise.
        """
        try:
            if not os.path.exists(self.local_path):
                logger.error(
                    "Cannot checkout: local path %s does not exist", self.local_path
                )
                return False

            subprocess.run(
                ["git", "-C", self.local_path, "fetch", "origin"],
                check=True,
                capture_output=True,
                text=True,
                timeout=60,
            )
            subprocess.run(
                ["git", "-C", self.local_path, "checkout", revision],
                check=True,
                capture_output=True,
                text=True,
                timeout=60,
            )
            return True
        except (subprocess.CalledProcessError, OSError) as e:
            logger.error("Git checkout failed: %s", getattr(e, "stderr", str(e)))
            return False

    def is_dirty(self) -> bool:
        """Check if the local repository has uncommitted changes.

        Returns:
            True if the repository is dirty, False otherwise.
        """
        try:
            if not os.path.exists(self.local_path):
                return False

            result = subprocess.run(
                ["git", "-C", self.local_path, "status", "--porcelain"],
                capture_output=True,
                text=True,
                check=True,
                timeout=10,
            )
            return bool(result.stdout.strip())
        except (subprocess.CalledProcessError, OSError):
            return False
