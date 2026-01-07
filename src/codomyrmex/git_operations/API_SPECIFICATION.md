# Git Operations - API Specification

## Introduction

This document specifies the Application Programming Interface (API) for the `git_operations` module. The module provides a comprehensive, production-ready interface for all Git operations within the Codomyrmex ecosystem, supporting complete Git workflows with 40+ operations covering all aspects of Git repository management.

**Note**: For complete detailed API documentation with all function signatures, parameters, return types, and examples, see [COMPLETE_API_DOCUMENTATION.md](./COMPLETE_API_DOCUMENTATION.md).

## Core Operations

### `check_git_availability() -> bool`

- **Description**: Verifies that Git is installed and accessible on the system.
- **Parameters**: None
- **Returns**: `bool` - True if Git is available, False otherwise
- **Raises**: None (returns False on errors)

### `is_git_repository(path: str = None) -> bool`

- **Description**: Checks if the specified path (or current directory) is a Git repository.
- **Parameters**:
    - `path` (str, optional): Path to check. Defaults to current working directory.
- **Returns**: `bool` - True if path is a Git repository, False otherwise
- **Raises**: None (returns False on errors)

### `initialize_git_repository(path: str, initial_commit: bool = True) -> bool`

- **Description**: Creates a new Git repository at the specified path with optional initial commit.
- **Parameters**:
    - `path` (str): Directory path where the repository will be created
    - `initial_commit` (bool, optional): Whether to create an initial commit with README.md. Defaults to True.
- **Returns**: `bool` - True if repository was created successfully, False otherwise
- **Raises**: None (returns False on errors)

### `clone_repository(url: str, destination: str, branch: str = None) -> bool`

- **Description**: Clones a remote Git repository to the specified local destination.
- **Parameters**:
    - `url` (str): Remote repository URL to clone
    - `destination` (str): Local directory path for the cloned repository
    - `branch` (str, optional): Specific branch to clone. Defaults to repository default.
- **Returns**: `bool` - True if repository was cloned successfully, False otherwise
- **Raises**: None (returns False on errors)

## Branch Operations

### `create_branch(branch_name: str, repository_path: str = None) -> bool`

- **Description**: Creates a new branch and switches to it.
- **Parameters**:
    - `branch_name` (str): Name of the new branch to create
    - `repository_path` (str, optional): Path to Git repository. Defaults to current directory.
- **Returns**: `bool` - True if branch was created successfully, False otherwise

### `switch_branch(branch_name: str, repository_path: str = None) -> bool`

- **Description**: Switches to an existing branch.
- **Parameters**:
    - `branch_name` (str): Name of the branch to switch to
    - `repository_path` (str, optional): Path to Git repository. Defaults to current directory.
- **Returns**: `bool` - True if branch switch was successful, False otherwise

### `get_current_branch(repository_path: str = None) -> Optional[str]`

- **Description**: Gets the name of the currently active branch.
- **Parameters**:
    - `repository_path` (str, optional): Path to Git repository. Defaults to current directory.
- **Returns**: `Optional[str]` - Name of the current branch, or None on error

### `merge_branch(source_branch: str, target_branch: str, repository_path: str = None) -> bool`

- **Description**: Merges source branch into target branch.
- **Parameters**:
    - `source_branch` (str): Branch to merge from
    - `target_branch` (str): Branch to merge into
    - `repository_path` (str, optional): Path to Git repository. Defaults to current directory.
- **Returns**: `bool` - True if merge was successful, False otherwise

### `rebase_branch(branch_name: str, base_branch: str, repository_path: str = None) -> bool`

- **Description**: Rebases a branch onto another branch.
- **Parameters**:
    - `branch_name` (str): Branch to rebase
    - `base_branch` (str): Branch to rebase onto
    - `repository_path` (str, optional): Path to Git repository. Defaults to current directory.
- **Returns**: `bool` - True if rebase was successful, False otherwise

## File Operations

### `add_files(file_paths: list[str], repository_path: str = None) -> bool`

- **Description**: Add files to the Git staging area.
- **Parameters**:
    - `file_paths` (list[str]): List of file paths to add
    - `repository_path` (str, optional): Path to Git repository. Defaults to current directory.
- **Returns**: `bool` - True if files were added successfully, False otherwise

### `commit_changes(message: str, repository_path: str = None) -> bool`

- **Description**: Commit staged changes with the given message.
- **Parameters**:
    - `message` (str): Commit message
    - `repository_path` (str, optional): Path to Git repository. Defaults to current directory.
- **Returns**: `bool` - True if commit was successful, False otherwise

### `get_status(repository_path: str = None) -> dict[str, Any]`

- **Description**: Get the current status of the repository.
- **Parameters**:
    - `repository_path` (str, optional): Path to Git repository. Defaults to current directory.
- **Returns**: `dict[str, Any]` - Dictionary containing status information (branch, changes, etc.)

### `get_diff(repository_path: str = None, staged: bool = False) -> str`

- **Description**: Get the diff of changes in the repository.
- **Parameters**:
    - `repository_path` (str, optional): Path to Git repository. Defaults to current directory.
    - `staged` (bool, optional): Whether to show staged changes. Defaults to False.
- **Returns**: `str` - Diff output as string

### `reset_changes(repository_path: str = None, mode: str = "mixed") -> bool`

- **Description**: Reset changes in the repository.
- **Parameters**:
    - `repository_path` (str, optional): Path to Git repository. Defaults to current directory.
    - `mode` (str, optional): Reset mode ("mixed", "soft", "hard"). Defaults to "mixed".
- **Returns**: `bool` - True if reset was successful, False otherwise

## Remote Operations

### `push_changes(remote: str = "origin", branch: str = None, repository_path: str = None) -> bool`

- **Description**: Push committed changes to a remote repository.
- **Parameters**:
    - `remote` (str, optional): Remote name. Defaults to "origin".
    - `branch` (str, optional): Branch to push. Defaults to current branch.
    - `repository_path` (str, optional): Path to Git repository. Defaults to current directory.
- **Returns**: `bool` - True if push was successful, False otherwise

### `pull_changes(remote: str = "origin", branch: str = None, repository_path: str = None) -> bool`

- **Description**: Pull changes from a remote repository.
- **Parameters**:
    - `remote` (str, optional): Remote name. Defaults to "origin".
    - `branch` (str, optional): Branch to pull. Defaults to current branch.
    - `repository_path` (str, optional): Path to Git repository. Defaults to current directory.
- **Returns**: `bool` - True if pull was successful, False otherwise

## History & Information

### `get_commit_history(repository_path: str = None, max_count: int = 10, branch: str = None) -> list[dict[str, Any]]`

- **Description**: Get commit history for the repository.
- **Parameters**:
    - `repository_path` (str, optional): Path to Git repository. Defaults to current directory.
    - `max_count` (int, optional): Maximum number of commits to return. Defaults to 10.
    - `branch` (str, optional): Branch to get history for. Defaults to current branch.
- **Returns**: `list[dict[str, Any]]` - List of commit dictionaries with metadata

## Tag Operations

### `create_tag(tag_name: str, message: str = None, repository_path: str = None) -> bool`

- **Description**: Create a Git tag.
- **Parameters**:
    - `tag_name` (str): Name of the tag
    - `message` (str, optional): Tag message
    - `repository_path` (str, optional): Path to Git repository. Defaults to current directory.
- **Returns**: `bool` - True if tag was created successfully, False otherwise

### `list_tags(repository_path: str = None) -> list[str]`

- **Description**: List all tags in the repository.
- **Parameters**:
    - `repository_path` (str, optional): Path to Git repository. Defaults to current directory.
- **Returns**: `list[str]` - List of tag names

## Stash Operations

### `stash_changes(message: str = None, repository_path: str = None) -> bool`

- **Description**: Stash uncommitted changes.
- **Parameters**:
    - `message` (str, optional): Stash message
    - `repository_path` (str, optional): Path to Git repository. Defaults to current directory.
- **Returns**: `bool` - True if stash was successful, False otherwise

### `apply_stash(stash_ref: str = None, repository_path: str = None) -> bool`

- **Description**: Apply a stash.
- **Parameters**:
    - `stash_ref` (str, optional): Stash reference (e.g., "stash@{0}"). Defaults to most recent.
    - `repository_path` (str, optional): Path to Git repository. Defaults to current directory.
- **Returns**: `bool` - True if stash was applied successfully, False otherwise

### `list_stashes(repository_path: str = None) -> list[dict[str, str]]`

- **Description**: List all stashes.
- **Parameters**:
    - `repository_path` (str, optional): Path to Git repository. Defaults to current directory.
- **Returns**: `list[dict[str, str]]` - List of stash dictionaries with metadata

## GitHub API Operations

The module also provides GitHub API integration through the `github_api` submodule. See `github_api.py` for functions like:
- `create_github_repository()`
- `create_pull_request()`
- `get_pull_requests()`
- `get_repository_info()`

## Visualization Integration

When `data_visualization` module is available, the following functions are provided:
- `create_git_analysis_report()`
- `visualize_git_branches()`
- `visualize_commit_activity()`
- `create_git_workflow_diagram()`

See `visualization_integration.py` for details.

## Data Models

### Repository Status Dictionary
Returned by `get_status()`:
```python
{
    "branch": str,           # Current branch name
    "is_dirty": bool,        # Whether there are uncommitted changes
    "untracked_files": list[str],
    "modified_files": list[str],
    "staged_files": list[str],
    "ahead_by": int,        # Commits ahead of remote
    "behind_by": int         # Commits behind remote
}
```

### Commit History Dictionary
Returned by `get_commit_history()`:
```python
{
    "sha": str,              # Full commit SHA
    "short_sha": str,        # Short commit SHA
    "message": str,          # Commit message
    "author": str,           # Author name
    "email": str,            # Author email
    "date": str,             # Commit date (ISO format)
    "timestamp": float       # Unix timestamp
}
```

## Authentication & Authorization

- **Credential Management**: The module relies on Git's underlying credential management system (SSH agent, Git Credential Manager, OS keychain). It does not directly handle or store credentials.
- **GitHub API**: Requires a GitHub Personal Access Token (PAT) stored in environment variables or Git credential helper.
- **Security**: See [SECURITY.md](./SECURITY.md) for detailed security considerations.

## Error Handling

All functions return `False` or `None` on failure rather than raising exceptions. Errors are logged via the `logging_monitoring` module. Check function return values and logs for error details.

## Rate Limiting

- **Git Operations**: No rate limiting (limited by system resources)
- **GitHub API**: Subject to GitHub API rate limits (5,000 requests/hour for authenticated requests)

## Versioning

This API follows the Codomyrmex project versioning strategy. API stability is maintained for public functions. Internal implementations may change without notice.

## Complete Documentation

For comprehensive documentation with detailed examples, parameter descriptions, and usage patterns, see:
- [COMPLETE_API_DOCUMENTATION.md](./COMPLETE_API_DOCUMENTATION.md) - Full API reference
- [USAGE_EXAMPLES.md](./USAGE_EXAMPLES.md) - Practical usage examples
- [SECURITY.md](./SECURITY.md) - Security considerations and best practices

## Navigation Links

- **Parent**: [Project Overview](../README.md)
- **Module Index**: [All Agents](../../AGENTS.md)
- **Documentation**: [Reference Guides](../../../docs/README.md)
- **Home**: [Root README](../../../README.md)
