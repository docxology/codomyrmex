from pathlib import Path
from typing import Optional
import logging
import shutil
import subprocess

from codomyrmex.git_operations.git_manager import (
from codomyrmex.logging_monitoring.logger_config import get_logger



try:
        clone_repository,
        is_git_repository,
        pull_changes,
    )
except ImportError:
    # Fallback functions defined below
    def clone_repository(url: str, destination: str, branch: Optional[str] = None) -> bool:
        """Fallback clone function."""
        try:
            cmd = ["git", "clone"]
            if branch:
                cmd.extend(["-b", branch])
            cmd.extend([url, str(destination)])
            subprocess.run(cmd, check=True, capture_output=True)
            return True
        except Exception:
            return False

    def is_git_repository(path: str) -> bool:
        """Fallback git check."""
        try:
            subprocess.run(
                ["git", "rev-parse", "--git-dir"],
                cwd=path,
                check=True,
                capture_output=True,
            )
            return True
        except Exception:
            return False

    def pull_changes(repository_path: str) -> bool:
        """Fallback pull function."""
        try:
            subprocess.run(
                ["git", "pull"],
                cwd=repository_path,
                check=True,
                capture_output=True,
            )
            return True
        except Exception:
            return False

logger = get_logger(__name__)


class SkillSync:
    """Handles syncing with upstream vibeship-spawner-skills repository."""

    def __init__(
        self,
        upstream_dir: Path,
        upstream_repo: str,
        upstream_branch: str = "main",
    ):
        """
        Initialize SkillSync.

        Args:
            upstream_dir: Directory where upstream skills are stored
            upstream_repo: URL of upstream repository
            upstream_branch: Branch to track
        """
        self.upstream_dir = Path(upstream_dir)
        self.upstream_repo = upstream_repo
        self.upstream_branch = upstream_branch
        logger.info(
            f"SkillSync initialized: {upstream_dir}, repo={upstream_repo}, branch={upstream_branch}"
        )

    def clone_upstream(self, force: bool = False) -> bool:
        """
        Clone the upstream repository.

        Args:
            force: If True, remove existing directory before cloning

        Returns:
            True if successful, False otherwise
        """
        if self.upstream_dir.exists():
            if force:
                logger.info(f"Removing existing upstream directory: {self.upstream_dir}")

                shutil.rmtree(self.upstream_dir)
            else:
                logger.warning(
                    f"Upstream directory already exists: {self.upstream_dir}. Use force=True to overwrite."
                )
                return False

        try:
            logger.info(f"Cloning upstream repository to {self.upstream_dir}")
            self.upstream_dir.parent.mkdir(parents=True, exist_ok=True)

            success = clone_repository(
                self.upstream_repo, str(self.upstream_dir), self.upstream_branch
            )

            if success:
                logger.info("Successfully cloned upstream repository")
            else:
                logger.error("Failed to clone upstream repository")
            return success

        except Exception as e:
            logger.error(f"Error cloning upstream repository: {e}")
            return False

    def pull_upstream(self) -> bool:
        """
        Pull latest changes from upstream repository.

        Returns:
            True if successful, False otherwise
        """
        if not self.upstream_dir.exists():
            logger.warning(
                f"Upstream directory does not exist: {self.upstream_dir}. Cloning instead."
            )
            return self.clone_upstream()

        if not is_git_repository(str(self.upstream_dir)):
            logger.warning(
                f"Upstream directory is not a git repository: {self.upstream_dir}. Cloning instead."
            )
            return self.clone_upstream(force=True)

        try:
            logger.info(f"Pulling latest changes from upstream: {self.upstream_dir}")
            success = pull_changes(str(self.upstream_dir))

            if success:
                logger.info("Successfully pulled upstream changes")
            else:
                logger.error("Failed to pull upstream changes")
            return success

        except Exception as e:
            logger.error(f"Error pulling upstream changes: {e}")
            return False

    def check_upstream_status(self) -> dict:
        """
        Check the status of the upstream repository.

        Returns:
            Dictionary with status information
        """
        status = {
            "exists": self.upstream_dir.exists(),
            "is_git_repo": False,
            "branch": None,
            "has_changes": False,
            "last_commit": None,
        }

        if not status["exists"]:
            return status

        if not is_git_repository(str(self.upstream_dir)):
            return status

        status["is_git_repo"] = True

        try:
            # Get current branch
            result = subprocess.run(
                ["git", "branch", "--show-current"],
                cwd=str(self.upstream_dir),
                capture_output=True,
                text=True,
                check=True,
            )
            status["branch"] = result.stdout.strip()

            # Check for uncommitted changes
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=str(self.upstream_dir),
                capture_output=True,
                text=True,
                check=True,
            )
            status["has_changes"] = bool(result.stdout.strip())

            # Get last commit hash
            result = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                cwd=str(self.upstream_dir),
                capture_output=True,
                text=True,
                check=True,
            )
            status["last_commit"] = result.stdout.strip()[:8]

        except Exception as e:
            logger.warning(f"Error checking upstream status: {e}")

        return status

    def get_upstream_version(self) -> Optional[str]:
        """
        Get the current version/commit of the upstream repository.

        Returns:
            Commit hash or None if unavailable
        """
        if not self.upstream_dir.exists() or not is_git_repository(str(self.upstream_dir)):
            return None

        try:
            result = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                cwd=str(self.upstream_dir),
                capture_output=True,
                text=True,
                check=True,
            )
            return result.stdout.strip()
        except Exception as e:
            logger.warning(f"Error getting upstream version: {e}")
            return None


