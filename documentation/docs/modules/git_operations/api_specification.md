---
sidebar_label: 'API Specification'
title: 'Git Operations - API Specification'
---

# Git Operations - API Specification

## Introduction

This API provides functions to interact with Git repositories. These functions can be used by other modules to automate Git tasks or to retrieve information from repositories. It typically wraps Git command-line operations or uses a library like GitPython.

## Functions / Interfaces

(These are conceptual Python functions. Actual implementation might vary.)

### Function: `git_clone(repo_url: str, local_path: str) -> bool`

- **Description**: Clones a remote Git repository to a local path.
- **Parameters**:
    - `repo_url` (str): The URL of the remote repository (HTTPS or SSH).
    - `local_path` (str): The local directory path to clone into.
- **Returns** (bool): `True` if cloning was successful, `False` otherwise.
- **Raises**: `GitCommandError` on failure.

### Function: `git_status(repo_path: str) -> dict`

- **Description**: Gets the status of a local Git repository (similar to `git status`).
- **Parameters**:
    - `repo_path` (str): Path to the local repository.
- **Returns** (dict): A dictionary containing status information, e.g.:
    ```json
    {
      "branch": "main",
      "is_dirty": true,
      "untracked_files": ["new_file.txt"],
      "modified_files": ["existing_file.py"],
      "staged_files": []
    }
    ```
- **Raises**: `NotAGitRepositoryError`, `GitCommandError`.

### Function: `git_add(repo_path: str, files: list[str] | str) -> bool`

- **Description**: Stages specified files or all changes.
- **Parameters**:
    - `repo_path` (str): Path to the local repository.
    - `files` (list[str] | str): A list of file paths to stage, or `"."` or `"*"` to stage all changes.
- **Returns** (bool): `True` if successful, `False` otherwise.
- **Raises**: `GitCommandError`.

### Function: `git_commit(repo_path: str, message: str) -> str | None`

- **Description**: Commits staged changes.
- **Parameters**:
    - `repo_path` (str): Path to the local repository.
    - `message` (str): The commit message.
- **Returns** (str | None): The commit hash if successful, `None` otherwise.
- **Raises**: `GitCommandError`.

### Function: `git_push(repo_path: str, remote: str = "origin", branch: str | None = None) -> bool`

- **Description**: Pushes committed changes to a remote repository.
- **Parameters**:
    - `repo_path` (str): Path to the local repository.
    - `remote` (str, optional): The name of the remote. Defaults to "origin".
    - `branch` (str | None, optional): The branch to push. Defaults to the current branch.
- **Returns** (bool): `True` if successful, `False` otherwise.
- **Raises**: `GitCommandError`.

### Function: `git_pull(repo_path: str, remote: str = "origin", branch: str | None = None) -> bool`

- **Description**: Fetches from and integrates with another repository or a local branch.
- **Parameters**:
    - `repo_path` (str): Path to the local repository.
    - `remote` (str, optional): The name of the remote. Defaults to "origin".
    - `branch` (str | None, optional): The branch to pull. Defaults to the current branch.
- **Returns** (bool): `True` if successful, `False` otherwise.
- **Raises**: `GitCommandError`.

### Function: `git_create_branch(repo_path: str, branch_name: str, checkout: bool = False) -> bool`

- **Description**: Creates a new branch.
- **Parameters**:
    - `repo_path` (str): Path to the local repository.
    - `branch_name` (str): The name for the new branch.
    - `checkout` (bool, optional): If `True`, checkout the new branch after creation. Defaults to `False`.
- **Returns** (bool): `True` if successful, `False` otherwise.
- **Raises**: `GitCommandError`.

### Function: `git_checkout_branch(repo_path: str, branch_name: str) -> bool`

- **Description**: Checks out an existing branch.
- **Parameters**:
    - `repo_path` (str): Path to the local repository.
    - `branch_name` (str): The name of the branch to checkout.
- **Returns** (bool): `True` if successful, `False` otherwise.
- **Raises**: `GitCommandError`.

## Data Models

### Model: `GitStatus` (Conceptual, for `git_status` return)
- `branch` (str): Current active branch.
- `is_dirty` (bool): Whether there are uncommitted changes.
- `untracked_files` (list[str]): List of untracked file paths.
- `modified_files` (list[str]): List of modified (unstaged) file paths.
- `staged_files` (list[str]): List of staged file paths.

## Error Handling

- Functions may raise specific exceptions like `NotAGitRepositoryError`, `GitCommandError` (which might contain stderr output), or `AuthenticationError` for remote operations.

## Authentication & Authorization

- Authentication for remote operations (clone, push, pull) relies on the underlying Git setup (e.g., SSH keys, credential manager).
- The API itself does not handle credentials directly.

## Versioning

- API function signatures will be versioned according to SemVer principles if changes are made. 