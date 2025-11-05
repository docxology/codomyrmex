"""
Git Operations Module for Codomyrmex.

The Git Operations module is designed to provide a standardized interface and a set
of tools for performing common Git actions programmatically within the Codomyrmex
ecosystem.

Integration:
- Uses `logging_monitoring` for all logging (ensure `setup_logging()` is called in your main app).
- Relies on `environment_setup` for environment and dependency checks.

Available functions:
Core Operations:
- check_git_availability
- is_git_repository
- initialize_git_repository
- clone_repository

Branch Operations:
- create_branch
- switch_branch
- get_current_branch
- merge_branch
- rebase_branch

File Operations:
- add_files
- commit_changes
- amend_commit
- get_status
- get_diff
- reset_changes

Remote Operations:
- push_changes
- pull_changes
- fetch_changes
- add_remote
- remove_remote
- list_remotes

History & Information:
- get_commit_history
- get_commit_history_filtered

Config Operations:
- get_config
- set_config

Advanced Operations:
- cherry_pick

Tag Operations:
- create_tag
- list_tags

Stash Operations:
- stash_changes
- apply_stash
- list_stashes

GitHub API Operations:
- create_github_repository
- delete_github_repository
- create_pull_request
- get_pull_requests
- get_pull_request
- get_repository_info

Visualization Integration:
- create_git_analysis_report
- visualize_git_branches
- visualize_commit_activity
- create_git_workflow_diagram
- analyze_repository_structure
- get_repository_metadata
"""

from codomyrmex.exceptions import CodomyrmexError

from .git_manager import (
    # File operations
    add_files,
    amend_commit,
    apply_stash,
    # Core operations
    check_git_availability,
    clone_repository,
    commit_changes,
    # Branch operations
    create_branch,
    # Tag operations
    create_tag,
    # History & information
    get_commit_history,
    get_commit_history_filtered,
    get_current_branch,
    get_diff,
    get_status,
    initialize_git_repository,
    is_git_repository,
    list_stashes,
    list_tags,
    merge_branch,
    pull_changes,
    # Remote operations
    add_remote,
    fetch_changes,
    list_remotes,
    push_changes,
    remove_remote,
    rebase_branch,
    reset_changes,
    # Stash operations
    stash_changes,
    switch_branch,
    # Config operations
    get_config,
    set_config,
    # Advanced operations
    cherry_pick,
)
from .github_api import (
    GitHubAPIError,
    # GitHub API operations
    create_github_repository,
    create_pull_request,
    delete_github_repository,
    get_pull_request,
    get_pull_requests,
    get_repository_info,
)

try:
    from .visualization_integration import (
        analyze_repository_structure,
        # Visualization integration
        create_git_analysis_report,
        create_git_workflow_diagram,
        get_repository_metadata,
        visualize_commit_activity,
        visualize_git_branches,
    )

    VISUALIZATION_INTEGRATION_AVAILABLE = True
except ImportError:
    VISUALIZATION_INTEGRATION_AVAILABLE = False

__all__ = [
    # Core operations
    "check_git_availability",
    "is_git_repository",
    "initialize_git_repository",
    "clone_repository",
    # Branch operations
    "create_branch",
    "switch_branch",
    "get_current_branch",
    "merge_branch",
    "rebase_branch",
    # File operations
    "add_files",
    "commit_changes",
    "amend_commit",
    "get_status",
    "get_diff",
    "reset_changes",
    # Remote operations
    "push_changes",
    "pull_changes",
    "fetch_changes",
    "add_remote",
    "remove_remote",
    "list_remotes",
    # History & information
    "get_commit_history",
    "get_commit_history_filtered",
    # Config operations
    "get_config",
    "set_config",
    # Advanced operations
    "cherry_pick",
    # Tag operations
    "create_tag",
    "list_tags",
    # Stash operations
    "stash_changes",
    "apply_stash",
    "list_stashes",
    # GitHub API operations
    "create_github_repository",
    "delete_github_repository",
    "create_pull_request",
    "get_pull_requests",
    "get_pull_request",
    "get_repository_info",
    "GitHubAPIError",
]

# Add visualization functions if available
if VISUALIZATION_INTEGRATION_AVAILABLE:
    __all__.extend(
        [
            # Visualization integration
            "create_git_analysis_report",
            "visualize_git_branches",
            "visualize_commit_activity",
            "create_git_workflow_diagram",
            "analyze_repository_structure",
            "get_repository_metadata",
        ]
    )
