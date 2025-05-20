# Git Operations - API Specification

## Introduction

This document specifies the Application Programming Interface (API) for the `git_operations` module. The API will consist of Python functions designed to interact with Git repositories programmatically. These functions will wrap common Git commands and provide structured output, facilitating Git automation within the Codomyrmex ecosystem.

<!-- TODO: As the module is implemented (e.g., in `git_wrapper.py` or `git_utils.py`), detail each public function here. -->

## Endpoints / Functions / Interfaces

(Detail each Python function intended for public use from this module. Use a consistent format.)

### Function: `example_git_operation()`
<!-- TODO: Replace this example with actual function specifications. -->

- **Source**: (e.g., `git_operations.git_wrapper.example_git_operation`)
- **Description**: (What this function does, e.g., "Clones a remote Git repository to a specified local path.")
- **Method**: N/A (Python function)
- **Path**: N/A (Importable function)
- **Parameters/Arguments**:
    - `repo_url` (str): "URL of the remote repository."
    - `local_path` (str): "Local directory to clone into."
    - `branch` (str, optional): "Specific branch to checkout after cloning. Defaults to the repository's default branch."
- **Request Body**: N/A
- **Returns/Response**:
    - (e.g., `Repository` object representing the cloned repository, or `None` on failure)
    - **Raises**: (e.g., `GitCloneError` if cloning fails, `InvalidPathError` if `local_path` is invalid)
- **Side Effects**: (e.g., Creates a directory and clones a Git repository into it. Modifies file system.)
- **Events Emitted**: N/A

<!-- TODO: Add more function specifications as they are designed and implemented. Examples might include:
  - `get_repository_status(local_path: str) -> RepositoryStatus`
  - `get_current_branch(local_path: str) -> str`
  - `checkout_branch(local_path: str, branch_name: str, create_new: bool = False)`
  - `commit_changes(local_path: str, message: str, author_name: str = None, author_email: str = None)`
  - `push_changes(local_path: str, remote_name: str = 'origin', branch_name: str = None)`
  - `pull_changes(local_path: str, remote_name: str = 'origin', branch_name: str = None)`
  - `list_branches(local_path: str, remote: bool = False) -> list[str]`
  - `get_commit_log(local_path: str, max_count: int = 10) -> list[CommitInfo]`
-->

## Data Models

<!-- TODO: Define any common data structures or models returned by or passed to the API functions. -->

### Model: `RepositoryStatus` (Example)
<!-- TODO: Replace or define as needed. -->
- `current_branch` (str): Name of the current active branch.
- `has_uncommitted_changes` (bool): True if there are modified, staged, or untracked files.
- `untracked_files` (list[str]): List of untracked files.
- `modified_files` (list[str]): List of modified (but not staged) files.
- `staged_files` (list[str]): List of files staged for commit.

### Model: `CommitInfo` (Example)
<!-- TODO: Replace or define as needed. -->
- `sha` (str): Full commit hash.
- `author_name` (str): Author's name.
- `author_email` (str): Author's email.
- `date` (datetime): Date of the commit.
- `message` (str): Commit message.

## Authentication & Authorization

<!-- TODO: Describe how authentication for remote Git operations is handled. 
For example:
This module relies on the underlying Git CLI's configuration for authentication with remote repositories (e.g., SSH keys, credential managers, PATs stored in Git config). Functions performing remote operations may fail if authentication is not properly configured. Refer to Git documentation and the `environment_setup` module for guidance on setting up Git credentials.
-->

## Rate Limiting

N/A (Operations are local or depend on remote Git server rate limits, not imposed by this module itself).

## Versioning

API functions will be versioned as part of the `git_operations` module, following the overall project's semantic versioning. Changes to function signatures or core behavior will be noted in the module's `CHANGELOG.md`. 