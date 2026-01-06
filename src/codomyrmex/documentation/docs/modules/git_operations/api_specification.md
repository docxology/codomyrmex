# Git Operations - API Specification

## Introduction

This document specifies the Application Programming Interface (API) for the `git_operations` module. The API will consist of Python functions designed to interact with Git repositories programmatically. These functions will wrap common Git commands and provide structured output, facilitating Git automation within the Codomyrmex ecosystem.


## Endpoints / Functions / Interfaces

The `git_operations` module provides a comprehensive API for local Git repository management, GitHub integration, and repository visualization.

### Core Repository Management

#### `check_git_availability() -> bool`
- **Description**: Checks if Git is installed and available in the system PATH.
- **Returns**: `True` if available, `False` otherwise.

#### `is_git_repository(path: str = None) -> bool`
- **Description**: Determines if the specified path (or current directory) is a Git repository.
- **Parameters**: `path` (str, optional): Target directory path.
- **Returns**: `True` if it's a Git repository.

#### `initialize_git_repository(path: str, initial_commit: bool = True) -> bool`
- **Description**: Initializes a new Git repository at the specified path.
- **Parameters**: 
    - `path` (str): Directory where the repo should be created.
    - `initial_commit` (bool): Whether to create an empty initial commit.
- **Returns**: `True` on success.

#### `clone_repository(url: str, destination: str, branch: str = None) -> bool`
- **Description**: Clones a remote repository to a local destination.
- **Parameters**:
    - `url` (str): Repository URL (HTTPS/SSH).
    - `destination` (str): Local path for the clone.
    - `branch` (str, optional): Specific branch to clone.
- **Returns**: `True` on success.

### Branching & Merging

#### `create_branch(branch_name: str, repository_path: str = None) -> bool`
- **Description**: Creates and switches to a new branch.
- **Parameters**:
    - `branch_name` (str): Name for the new branch.
    - `repository_path` (str, optional): Path to the repo.
- **Returns**: `True` on success.

#### `switch_branch(branch_name: str, repository_path: str = None) -> bool`
- **Description**: Switches to an existing branch.
- **Parameters**: `branch_name` (str): Target branch name.
- **Returns**: `True` on success.

#### `get_current_branch(repository_path: str = None) -> str`
- **Description**: Retrieves the name of the currently active branch.
- **Returns**: Current branch name or `None` if operation fails.

#### `merge_branch(source_branch: str, target_branch: str = None, repository_path: str = None, strategy: str = None) -> bool`
- **Description**: Merges a source branch into the target (or current) branch.
- **Parameters**:
    - `source_branch` (str): Branch to merge from.
    - `target_branch` (str, optional): Destination branch.
- **Returns**: `True` if merge succeeded without conflicts.

### File & Commit Operations

#### `add_files(file_paths: list[str], repository_path: str = None) -> bool`
- **Description**: Stages files for commit (`git add`).
- **Parameters**: `file_paths` (list[str]): List of paths to stage.
- **Returns**: `True` on success.

#### `commit_changes(message: str, repository_path: str = None, author_name: str = None, author_email: str = None, stage_all: bool = True, file_paths: list[str] = None) -> Optional[str]`
- **Description**: Creates a new commit with staged or specified changes.
- **Parameters**:
    - `message` (str): The commit message.
    - `stage_all` (bool): If true, stages all tracked changes before committing.
    - `file_paths` (list[str]): Specific files to include in this commit.
- **Returns**: The commit hash (SHA-1) on success, `None` otherwise.

#### `get_status(repository_path: str = None) -> dict[str, Any]`
- **Description**: Retrieves structured status of the repository.
- **Returns**: Dictionary containing branch name, staged/unstaged files, and untracked files.

### Remote Operations

#### `push_changes(remote: str = "origin", branch: str = None, repository_path: str = None) -> bool`
- **Description**: Pushes local commits to a remote repository.
- **Returns**: `True` on success.

#### `pull_changes(remote: str = "origin", branch: str = None, repository_path: str = None) -> bool`
- **Description**: Pulls and merges changes from a remote branch.
- **Returns**: `True` on success.

### GitHub Integration

#### `create_pull_request(repo_owner: str, repo_name: str, head: str, base: str, title: str, body: str) -> dict`
- **Description**: Creates a new Pull Request on GitHub.
- **Returns**: Dictionary containing PR details from GitHub API.

## Data Models

### Model: `RepositoryStatus`
Represents the current state of a Git workspace as returned by `get_status()`.
- `branch` (str): Name of the current branch.
- `staged` (list[str]): Files staged for the next commit.
- `unstaged` (list[str]): Modified files not yet staged.
- `untracked` (list[str]): New files not yet tracked by Git.
- `is_dirty` (bool): `True` if there are any uncommitted changes.

### Model: `CommitInfo`
Metadata for a single commit returned in history listings.
- `hash` (str): Full SHA-1 commit hash.
- `author` (str): Author name.
- `date` (str): ISO 8601 formatted date.
- `message` (str): Commit message.

## Authentication & Authorization

This module interacts with Git remotes and the GitHub API.

1.  **Git Operations**: Relies on the local environment's Git configuration (SSH keys or Credential Manager).
2.  **GitHub API**: Requires a `GITHUB_TOKEN` environment variable for authenticated requests.

## Rate Limiting

- **GitHub API**: Subject to GitHub's REST API rate limits (typically 5,000 requests per hour for authenticated users).

## Versioning

This API follows semantic versioning aligned with the `codomyrmex` package.

## Navigation Links

- **Parent**: [Project Overview](../README.md)
- **Module Index**: [All Agents](../../AGENTS.md)
- **Documentation**: [Reference Guides](../../docs/README.md)
- **Home**: [Root README](../../../README.md)

## Authentication & Authorization

This module, when performing operations that interact with remote Git repositories (e.g., `clone` of private repos, `fetch`, `pull`, `push`), relies on the underlying Git command-line tool's configuration for authentication. This means that the environment where scripts using this module are run must have Git credentials configured appropriately.

Common methods include:
-   **SSH Keys**: Using SSH URLs for remotes (e.g., `git@github.com:user/repo.git`) with an SSH key pair configured and `ssh-agent` running.
-   **HTTPS with Credential Managers**: For HTTPS URLs (e.g., `https://github.com/user/repo.git`), Git can use a platform-specific credential manager (like Git Credential Manager Core) to securely store and provide usernames/passwords or Personal Access Tokens (PATs).
-   **Personal Access Tokens (PATs)**: For HTTPS, PATs can often be used in place of passwords, especially with services like GitHub, GitLab, or Bitbucket. These can be configured via credential managers or sometimes directly in Git configuration (though direct storage in config is less secure).
-   **Environment Variables**: Some CI/CD systems or specific tools might use environment variables (e.g., `GIT_ASKPASS` scripts, or by passing tokens directly to `git` commands if supported by the wrapper functions in this module - though this requires careful handling).

It is the responsibility of the user or the calling application to ensure that Git authentication is correctly set up in the execution environment. This `git_operations` module itself does not directly handle or store credentials like API keys or passwords. 

Refer to Git documentation and the `environment_setup` module for guidance on setting up Git credentials securely. Functions performing remote operations may fail with `AuthenticationError` or similar exceptions if authentication is not properly configured or fails.

## Rate Limiting

N/A (Operations are local or depend on remote Git server rate limits, not imposed by this module itself).

## Versioning

API functions will be versioned as part of the `git_operations` module, following the overall project's semantic versioning. Changes to function signatures or core behavior will be noted in the module's `CHANGELOG.md`. 
## Navigation Links

- **Parent**: [Project Overview](../README.md)
- **Module Index**: [All Agents](../../AGENTS.md)
- **Documentation**: [Reference Guides](../../docs/README.md)
- **Home**: [Root README](../../../README.md)
