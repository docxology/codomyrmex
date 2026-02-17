"""
Git Operations Module for Codomyrmex.

The Git Operations module provides a standardized interface and tools for performing
Git actions programmatically within the Codomyrmex ecosystem.

Integration:
- Uses `logging_monitoring` for all logging (ensure `setup_logging()` is called in your main app).
- Relies on `environment_setup` for environment and dependency checks.
"""

# Shared schemas for cross-module interop
try:
    from codomyrmex.validation.schemas import Result, ResultStatus
except ImportError:
    Result = None
    ResultStatus = None

from codomyrmex.exceptions import CodomyrmexError

# GitHub API Operations
from .api.github import (
    GitHubAPIError,
    # GitHub API operations
    create_github_repository,
    create_pull_request,
    delete_github_repository,
    get_pull_request,
    get_pull_requests,
    get_repository_info,
)

# Core Git Operations
from .core.git import (
    # File operations
    add_files,
    # Remote operations
    add_remote,
    amend_commit,
    apply_stash,
    # Core operations
    check_git_availability,
    # Advanced operations
    cherry_pick,
    clone_repository,
    commit_changes,
    # Branch operations
    create_branch,
    # Tag operations
    create_tag,
    fetch_changes,
    # History & information
    get_commit_history,
    # Config operations
    get_config,
    get_current_branch,
    get_diff,
    get_status,
    initialize_git_repository,
    is_git_repository,
    list_remotes,
    list_stashes,
    list_tags,
    merge_branch,
    pull_changes,
    push_changes,
    rebase_branch,
    remove_remote,
    reset_changes,
    set_config,
    # Stash operations
    stash_changes,
    switch_branch,
)

# Metadata Management
from .core.metadata import (
    CloneStatus,
    RepositoryMetadata,
    RepositoryMetadataManager,
)

# Repository Management
from .core.repository import (
    Repository,
    RepositoryManager,
    RepositoryType,
)

# Visualization Integration
try:
    from .api.visualization import (
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

def cli_commands():
    """Return CLI commands for the git_operations module."""
    def _show_status():
        import os
        try:
            status = get_status(os.getcwd())
            print("Git status:")
            if isinstance(status, dict):
                for key, value in status.items():
                    print(f"  {key}: {value}")
            else:
                print(f"  {status}")
        except Exception as e:
            print(f"Error getting git status: {e}")

    def _show_info():
        import os
        cwd = os.getcwd()
        try:
            is_repo = is_git_repository(cwd)
            print(f"Path: {cwd}")
            print(f"Is git repository: {is_repo}")
            if is_repo:
                branch = get_current_branch(cwd)
                print(f"Current branch: {branch}")
                remotes = list_remotes(cwd)
                print(f"Remotes: {remotes}")
        except Exception as e:
            print(f"Error getting repo info: {e}")

    return {
        "status": _show_status,
        "info": _show_info,
    }


__all__ = [
    "cli_commands",
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
    # Repository Management
    "RepositoryManager",
    "RepositoryType",
    "Repository",
    # Metadata Management
    "RepositoryMetadataManager",
    "RepositoryMetadata",
    "CloneStatus",
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
