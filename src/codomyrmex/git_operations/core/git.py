"""
Core module for executing Git operations.
"""

import time

from codomyrmex.logging_monitoring.core.logger_config import get_logger, setup_logging
from codomyrmex.performance import monitor_performance, performance_context

from .commands.branching import (
    create_branch,
    delete_branch,
    get_current_branch,
    switch_branch,
)
from .commands.commit import amend_commit, cherry_pick, commit_changes, revert_commit
from .commands.config import get_config, set_config
from .commands.history import (
    get_blame,
    get_commit_details,
    get_commit_history,
    get_commit_history_filtered,
)
from .commands.merge import merge_branch, rebase_branch
from .commands.remote import (
    add_remote,
    fetch_remote,
    list_remotes,
    prune_remote,
    remove_remote,
)
from .commands.repository import (
    check_git_availability,
    clone_repository,
    initialize_git_repository,
    is_git_repository,
)
from .commands.stash import apply_stash, list_stashes, stash_changes
from .commands.status import (
    add_files,
    clean_repository,
    get_diff,
    get_diff_files,
    get_status,
    reset_changes,
)
from .commands.submodules import init_submodules, update_submodules
from .commands.sync import fetch_changes, pull_changes, push_changes
from .commands.tags import create_tag, list_tags

logger = get_logger(__name__)

try:
    PERFORMANCE_MONITORING_AVAILABLE = True
except ImportError:
    logger.warning("Performance monitoring not available - decorators will be no-op")
    PERFORMANCE_MONITORING_AVAILABLE = False

    # Create no-op decorators
    def monitor_performance(*args, **kwargs):
        """Decorator for performance monitoring (fallback)."""
        def decorator(func):
            """Decorator."""
            return func
        return decorator

    class performance_context:
        """
        A class for handling performance_context operations.
        """
        def __init__(self, context_name: str = "unknown_context", *args, **kwargs):
            """Initialize performance context (fallback)."""
            self.context_name = context_name
            self.start_time = 0

        def __enter__(self):
            """Enter context."""
            self.start_time = time.time()
            return self

        def __exit__(self, exc_type, exc_val, exc_tb):
            """Exit context."""
            duration = time.time() - self.start_time
            logger.debug(f"Exiting performance context: {self.context_name} (Duration: {duration:.4f}s)")

__all__ = [
    "create_branch",
    "switch_branch",
    "delete_branch",
    "get_current_branch",
    "commit_changes",
    "amend_commit",
    "revert_commit",
    "cherry_pick",
    "add_remote",
    "remove_remote",
    "list_remotes",
    "fetch_remote",
    "prune_remote",
    "push_changes",
    "pull_changes",
    "fetch_changes",
    "get_status",
    "get_diff",
    "get_diff_files",
    "clean_repository",
    "reset_changes",
    "add_files",
    "get_commit_history",
    "get_commit_history_filtered",
    "get_commit_details",
    "get_blame",
    "check_git_availability",
    "is_git_repository",
    "initialize_git_repository",
    "clone_repository",
    "create_tag",
    "list_tags",
    "stash_changes",
    "apply_stash",
    "list_stashes",
    "merge_branch",
    "rebase_branch",
    "get_config",
    "set_config",
    "init_submodules",
    "update_submodules",
]

if __name__ == "__main__":
    # Ensure logging is set up when script is run directly
    setup_logging()
    logger.info("Executing git_manager.py directly for testing example.")

    # Example usage
    if check_git_availability():
        logger.info("Git operations available. Testing basic functionality...")

        # Test repository detection
        is_repo = is_git_repository()
        logger.info(f"Current directory is Git repository: {is_repo}")

        if is_repo:
            # Test getting status
            status = get_status()
            logger.info(f"Repository status: {status}")

            # Test getting current branch
            branch = get_current_branch()
            logger.info(f"Current branch: {branch}")

            # Test getting commit history
            commits = get_commit_history(5)
            logger.info(f"Recent commits: {len(commits)}")
    else:
        logger.warning("Git is not available. Cannot test Git operations.")
