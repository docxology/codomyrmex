"""
Git Operations Module for Codomyrmex.

The Git Operations module is designed to provide a standardized interface and a set
of tools for performing common Git actions programmatically within the Codomyrmex
ecosystem.

Integration:
- Uses `logging_monitoring` for all logging (ensure `setup_logging()` is called in your main app).
- Relies on `environment_setup` for environment and dependency checks.

Available functions:
- check_git_availability
- is_git_repository
- initialize_git_repository
- clone_repository
- create_branch
- switch_branch
- get_current_branch
- add_files
- commit_changes
- push_changes
- pull_changes
- get_status
- get_commit_history
"""

from .git_manager import (
    check_git_availability,
    is_git_repository,
    initialize_git_repository,
    clone_repository,
    create_branch,
    switch_branch,
    get_current_branch,
    add_files,
    commit_changes,
    push_changes,
    pull_changes,
    get_status,
    get_commit_history,
)

__all__ = [
    'check_git_availability',
    'is_git_repository',
    'initialize_git_repository',
    'clone_repository',
    'create_branch',
    'switch_branch',
    'get_current_branch',
    'add_files',
    'commit_changes',
    'push_changes',
    'pull_changes',
    'get_status',
    'get_commit_history',
] 