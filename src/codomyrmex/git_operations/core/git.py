"""
Core module for executing Git operations.
"""

import os

from codomyrmex.logging_monitoring import get_logger, setup_logging
from codomyrmex.performance import PERFORMANCE_MONITOR_AVAILABLE

if PERFORMANCE_MONITOR_AVAILABLE:
    pass

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
    "add_files",
    "add_remote",
    "amend_commit",
    "apply_stash",
    "check_git_availability",
    "cherry_pick",
    "clean_repository",
    "clone_repository",
    "commit_changes",
    "create_branch",
    "create_tag",
    "delete_branch",
    "fetch_changes",
    "fetch_remote",
    "get_blame",
    "get_commit_details",
    "get_commit_history",
    "get_commit_history_filtered",
    "get_config",
    "get_current_branch",
    "get_diff",
    "get_diff_files",
    "get_status",
    "init_submodules",
    "initialize_git_repository",
    "is_git_repository",
    "list_branches",
    "list_remotes",
    "list_stashes",
    "list_tags",
    "merge_branch",
    "prune_remote",
    "pull_changes",
    "push_changes",
    "rebase_branch",
    "remove_remote",
    "reset_changes",
    "revert_commit",
    "set_config",
    "stash_changes",
    "switch_branch",
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
        logger.info("Current directory is Git repository: %s", is_repo)

        if is_repo:
            # Test getting status
            status = get_status(os.getcwd())
            logger.info("Repository status: %s", status)

            # Test getting current branch
            branch = get_current_branch(os.getcwd())
            logger.info("Current branch: %s", branch)

            # Test getting commit history
            commits = get_commit_history(limit=5, repository_path=os.getcwd())
            logger.info("Recent commits: %s", len(commits))
    else:
        logger.warning("Git is not available. Cannot test Git operations.")
