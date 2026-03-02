"""
Core module for executing Git operations.
"""

import os

from codomyrmex.logging_monitoring.core.logger_config import get_logger, setup_logging
from codomyrmex.performance import PERFORMANCE_MONITOR_AVAILABLE

if PERFORMANCE_MONITOR_AVAILABLE:
    from codomyrmex.performance import (  # noqa: F401
        monitor_performance,
        performance_context,
    )

from .commands.branching import (
    create_branch,
    delete_branch,
    get_current_branch,
    list_branches,
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
# PERFORMANCE_MONITORING_AVAILABLE reflects actual psutil availability at import time.
# monitor_performance and performance_context are only defined when this is True.
PERFORMANCE_MONITORING_AVAILABLE = PERFORMANCE_MONITOR_AVAILABLE

__all__ = [
    "create_branch",
    "switch_branch",
    "delete_branch",
    "get_current_branch",
    "list_branches",
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
    logger.info("Executing git.py directly for testing example.")

    # Example usage
    if check_git_availability():
        logger.info("Git operations available. Testing basic functionality...")

        # Test repository detection
        is_repo = is_git_repository(os.getcwd())
        logger.info(f"Current directory is Git repository: {is_repo}")

        if is_repo:
            # Test getting status
            status = get_status(os.getcwd())
            logger.info(f"Repository status: {status}")

            # Test getting current branch
            branch = get_current_branch(os.getcwd())
            logger.info(f"Current branch: {branch}")

            # Test getting commit history
            commits = get_commit_history(limit=5, repository_path=os.getcwd())
            logger.info(f"Recent commits: {len(commits)}")
    else:
        logger.warning("Git is not available. Cannot test Git operations.")
