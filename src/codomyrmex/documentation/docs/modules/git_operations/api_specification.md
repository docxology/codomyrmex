# Git Operations - API Specification

## Introduction

This document specifies the Application Programming Interface (API) for the `git_operations` module. The API will consist of Python functions designed to interact with Git repositories programmatically. These functions will wrap common Git commands and provide structured output, facilitating Git automation within the Codomyrmex ecosystem.

<!-- TODO: As the module is implemented (e.g., in `git_wrapper.py` or `git_utils.py`), detail each public function here. -->

## Endpoints / Functions / Interfaces

(Detail each Python function intended for public use from this module. Use a consistent format.)

<!-- 
  Potential function specifications for future implementation. 
  These would be defined in, for example, `git_operations.git_wrapper` or `git_operations.git_utils`.

### Function: `get_repository_status(local_path: str) -> RepositoryStatus`
- **Description**: Retrieves the current status of the Git repository at `local_path`.
- **Parameters**: `local_path` (str): Path to the local Git repository.
- **Returns**: `RepositoryStatus` object detailing current branch, changes, etc.
- **Raises**: `NotAGitRepositoryError` if `local_path` is not a Git repository.

### Function: `get_current_branch(local_path: str) -> str`
- **Description**: Gets the name of the currently active branch.
- **Parameters**: `local_path` (str): Path to the local Git repository.
- **Returns**: Name of the current branch as a string.
- **Raises**: `NotAGitRepositoryError`.

### Function: `checkout_branch(local_path: str, branch_name: str, create_new: bool = False)`
- **Description**: Checks out an existing branch or creates and checks out a new branch.
- **Parameters**:
    - `local_path` (str): Path to the local Git repository.
    - `branch_name` (str): Name of the branch to checkout or create.
    - `create_new` (bool, optional): If True, creates `branch_name` if it doesn't exist. Defaults to False.
- **Returns**: True on success, False on failure.
- **Raises**: `NotAGitRepositoryError`, `BranchCheckoutError`.

### Function: `commit_changes(local_path: str, message: str, author_name: str = None, author_email: str = None, stage_all: bool = True)`
- **Description**: Stages changes and creates a commit.
- **Parameters**:
    - `local_path` (str): Path to the local Git repository.
    - `message` (str): Commit message.
    - `author_name` (str, optional): Override Git config for author name.
    - `author_email` (str, optional): Override Git config for author email.
    - `stage_all` (bool, optional): If True, stages all tracked, modified files (`git add -u`) before committing. Defaults to True.
- **Returns**: SHA of the new commit on success, None on failure.
- **Raises**: `NotAGitRepositoryError`, `CommitError`.

### Function: `push_changes(local_path: str, remote_name: str = 'origin', branch_name: str = None, set_upstream: bool = False)`
- **Description**: Pushes local commits to a remote repository.
- **Parameters**:
    - `local_path` (str): Path to the local Git repository.
    - `remote_name` (str, optional): Name of the remote. Defaults to 'origin'.
    - `branch_name` (str, optional): Name of the branch to push. Defaults to the current branch.
    - `set_upstream` (bool, optional): If True, adds `--set-upstream` to the push command. Defaults to False.
- **Returns**: True on success, False on failure.
- **Raises**: `NotAGitRepositoryError`, `PushError`.

### Function: `pull_changes(local_path: str, remote_name: str = 'origin', branch_name: str = None)`
- **Description**: Fetches changes from a remote and merges them into the current or specified branch.
- **Parameters**:
    - `local_path` (str): Path to the local Git repository.
    - `remote_name` (str, optional): Name of the remote. Defaults to 'origin'.
    - `branch_name` (str, optional): Name of the branch to pull into. Defaults to the current branch.
- **Returns**: True on success, False on failure.
- **Raises**: `NotAGitRepositoryError`, `PullError`.

### Function: `list_branches(local_path: str, remote: bool = False) -> list[str]`
- **Description**: Lists local or remote branches.
- **Parameters**:
    - `local_path` (str): Path to the local Git repository.
    - `remote` (bool, optional): If True, lists remote branches. Defaults to False (local branches).
- **Returns**: A list of branch names.
- **Raises**: `NotAGitRepositoryError`.

### Function: `get_commit_log(local_path: str, max_count: int = 10, branch: str = None) -> list[CommitInfo]`
- **Description**: Retrieves commit history for the repository or a specific branch.
- **Parameters**:
    - `local_path` (str): Path to the local Git repository.
    - `max_count` (int, optional): Maximum number of commits to return. Defaults to 10.
    - `branch` (str, optional): Specific branch to get log for. Defaults to current branch.
- **Returns**: A list of `CommitInfo` objects.
- **Raises**: `NotAGitRepositoryError`.

-->

## Data Models

<!-- TODO: Define any common data structures or models returned by or passed to the API functions. These are examples. -->

### Model: `RepositoryStatus` (Example)
- `current_branch` (str): Name of the current active branch.
- `is_dirty` (bool): True if there are any uncommitted changes (staged, unstaged, or untracked).
- `untracked_files` (list[str]): List of untracked files.
- `modified_files` (list[str]): List of modified (but not staged) files.
- `staged_files` (list[str]): List of files staged for commit.
- `ahead_by` (int): Number of commits the local branch is ahead of its remote counterpart.
- `behind_by` (int): Number of commits the local branch is behind its remote counterpart.

### Model: `CommitInfo` (Example)
- `sha` (str): Full commit hash.
- `short_sha` (str): Short commit hash (e.g., first 7 characters).
- `author_name` (str): Author's name.
- `author_email` (str): Author's email.
- `date` (str): Date of the commit (ISO 8601 format).
- `message_subject` (str): First line of the commit message.
- `message_body` (str, optional): Rest of the commit message.

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