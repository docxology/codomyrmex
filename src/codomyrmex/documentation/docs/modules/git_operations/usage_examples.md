# Git Operations - Usage Examples

This document provides conceptual usage examples for the `git_operations` module, assuming the future implementation of functions outlined in its `API_SPECIFICATION.md`. These examples showcase how the Python API could be used to automate common Git tasks.

**Note**: The functions and classes (`GitRepository`, `RepositoryStatus`, `CommitInfo`, etc.) used below are illustrative and depend on the final implementation of the module (e.g., within a `git_wrapper.py` or `git_utils.py` file).

## Prerequisites

- Ensure the `git` command-line tool is installed and in your PATH.
- Your Python environment should be set up as per `environment_setup/README.md`.
- For operations involving remotes, ensure Git authentication (SSH keys, credential manager) is configured.
- The `git_operations` module (and any dependencies like `GitPython`) would need to be available.

```python
# Conceptual imports - actual module structure may vary
# from git_operations.git_wrapper import (
#     get_repository_status,
#     get_current_branch,
#     checkout_branch,
#     commit_changes,
#     push_changes,
#     list_branches,
#     get_commit_log
# )
# from git_operations.repository import RepositoryStatus, CommitInfo # Example data classes
# from git_operations.exceptions import NotAGitRepositoryError, GitCommandError

# For these examples, we'll assume functions are available directly
# and a local_repo_path variable points to a test Git repository.
local_repo_path = "/path/to/your/local/git/repository" 
# In real tests, you would create/clone a temporary repository.
```

## Example 1: Checking Repository Status

Showcases how to get the status of a local Git repository.

```python
# Placeholder for actual function call
def get_repository_status(local_path: str):
    # This would interact with Git to get status
    print(f"Simulating get_repository_status for {local_path}")
    # In a real implementation, return a RepositoryStatus object
    class MockRepositoryStatus:
        current_branch = "main"
        is_dirty = True
        untracked_files = ["new_file.txt"]
        modified_files = ["modified_script.py"]
        staged_files = []
        ahead_by = 0
        behind_by = 0
    return MockRepositoryStatus()

try:
    status = get_repository_status(local_repo_path)
    print(f"Current branch: {status.current_branch}")
    if status.is_dirty:
        print("Repository has uncommitted changes.")
        if status.untracked_files:
            print(f"  Untracked files: {status.untracked_files}")
        if status.modified_files:
            print(f"  Modified files (not staged): {status.modified_files}")
        if status.staged_files:
            print(f"  Staged files: {status.staged_files}")
    else:
        print("Repository is clean.")
except Exception as e: # Replace with specific exceptions like NotAGitRepositoryError
    print(f"Error getting status: {e}")
```

### Expected Outcome (Conceptual)

```
Simulating get_repository_status for /path/to/your/local/git/repository
Current branch: main
Repository has uncommitted changes.
  Untracked files: ['new_file.txt']
  Modified files (not staged): ['modified_script.py']
```

## Example 2: Creating a New Feature Branch and Making a Commit

Illustrates creating a new branch, making a conceptual commit, and checking status.

```python
# Placeholder for actual function calls
def checkout_branch(local_path: str, branch_name: str, create_new: bool = False):
    action = "Creating and checking out" if create_new else "Checking out"
    print(f"Simulating: {action} branch '{branch_name}' in {local_path}")
    return True # Assume success

def commit_changes(local_path: str, message: str, stage_all: bool = True):
    print(f"Simulating: Staging all ({stage_all}) and committing in {local_path} with message: '{message}'")
    return "mock_commit_sha_1234567" # Assume success, return mock SHA

feature_branch_name = "feature/add-example-tool"
commit_message = "feat: Add initial structure for example tool"

print(f"\n--- Scenario: Creating branch '{feature_branch_name}' ---")
try:
    if checkout_branch(local_repo_path, feature_branch_name, create_new=True):
        print(f"Successfully checked out new branch: {feature_branch_name}")
        
        # Simulate making some file changes here, then committing
        # For example, create/modify a file, then:
        # open(os.path.join(local_repo_path, "new_tool.py"), "w").write("# New tool code")
        
        commit_sha = commit_changes(local_repo_path, commit_message, stage_all=True)
        if commit_sha:
            print(f"Successfully committed changes. New commit SHA: {commit_sha}")
        else:
            print("Failed to commit changes.")
            
        # Verify status again (conceptually)
        status_after_commit = get_repository_status(local_repo_path)
        print(f"Status on branch '{status_after_commit.current_branch}': Is dirty? {status_after_commit.is_dirty}")
    else:
        print(f"Failed to checkout branch {feature_branch_name}")

except Exception as e: # Replace with specific exceptions
    print(f"Error during feature branch workflow: {e}")
```

### Expected Outcome (Conceptual)

```
--- Scenario: Creating branch 'feature/add-example-tool' ---
Simulating: Creating and checking out branch 'feature/add-example-tool' in /path/to/your/local/git/repository
Successfully checked out new branch: feature/add-example-tool
Simulating: Staging all (True) and committing in /path/to/your/local/git/repository with message: 'feat: Add initial structure for example tool'
Successfully committed changes. New commit SHA: mock_commit_sha_1234567
Simulating get_repository_status for /path/to/your/local/git/repository
Status on branch 'main': Is dirty? True
```
*(Note: The `status_after_commit.current_branch` might still show "main" or the new branch name depending on how the mock `get_repository_status` is updated or if `checkout_branch` changes a global mock state, which it doesn't in this simplified example. A real implementation would reflect the new branch.)*

## Example 3: Listing Branches and Viewing Commit Log

Demonstrates how to list branches and view recent commit history.

```python
# Placeholder for actual function calls
def list_branches(local_path: str, remote: bool = False):
    branch_type = "remote" if remote else "local"
    print(f"Simulating: Listing {branch_type} branches for {local_path}")
    if remote:
        return ["origin/main", "origin/develop", "origin/feature/some-feature"]
    else:
        return ["main", "develop", "feature/add-example-tool"]

def get_commit_log(local_path: str, max_count: int = 5, branch: str = None):
    log_for = f"branch '{branch}'" if branch else "current branch"
    print(f"Simulating: Getting commit log (top {max_count}) for {log_for} in {local_path}")
    class MockCommitInfo:
        def __init__(self, sha, msg, author):
            self.short_sha = sha[:7]
            self.message_subject = msg
            self.author_name = author
            self.date = "2023-10-26T10:00:00Z"
    return [
        MockCommitInfo("fedcba9876543210", "fix: Correct an issue in main", "Dev One"),
        MockCommitInfo("abcdef1234567890", "feat: Implement core feature X", "Dev Two"),
    ]

print(f"\n--- Scenario: Listing branches and log ---")
try:
    local_branches = list_branches(local_repo_path)
    print(f"Local branches: {local_branches}")
    
    remote_branches = list_branches(local_repo_path, remote=True)
    print(f"Remote branches: {remote_branches}")
    
    print("\nRecent commits on current branch (or default):")
    commits = get_commit_log(local_repo_path, max_count=3)
    for commit in commits:
        print(f"  - {commit.short_sha} - {commit.message_subject} ({commit.author_name})")
        
except Exception as e: # Replace with specific exceptions
    print(f"Error listing branches or log: {e}")
```

### Expected Outcome (Conceptual)

```
--- Scenario: Listing branches and log ---
Simulating: Listing local branches for /path/to/your/local/git/repository
Local branches: ['main', 'develop', 'feature/add-example-tool']
Simulating: Listing remote branches for /path/to/your/local/git/repository
Remote branches: ['origin/main', 'origin/develop', 'origin/feature/some-feature']

Recent commits on current branch (or default):
Simulating: Getting commit log (top 3) for current branch in /path/to/your/local/git/repository
  - fedcba9 - fix: Correct an issue in main (Dev One)
  - abcdef1 - feat: Implement core feature X (Dev Two)
```

## Common Pitfalls & Troubleshooting (Anticipated)

- **Issue**: `NotAGitRepositoryError` (or similar) when providing `local_repo_path`.
  - **Solution**: Ensure the path provided to the functions is a valid Git repository (contains a `.git` directory). Clone or initialize one if necessary.

- **Issue**: Authentication errors when interacting with remotes (`push_changes`, `pull_changes`).
  - **Solution**: Verify that your Git command-line environment is correctly configured for authentication with the remote repository (SSH keys, HTTPS PATs with a credential manager). This module relies on the underlying Git setup. Refer to `API_SPECIFICATION.md` section on Authentication.

- **Issue**: Operations fail due to local uncommitted changes (e.g., trying to `checkout_branch` when the working directory is dirty).
  - **Solution**: Some Git operations require a clean working directory. Use `get_repository_status()` to check for uncommitted changes and potentially commit or stash them before retrying the operation. API functions should ideally raise specific errors in such cases (e.g., `DirtyWorkingDirectoryError`).

- **Issue**: Incorrect author for commits made by automated scripts.
  - **Solution**: Ensure `git config user.name` and `git config user.email` are set in the environment where the script runs. Alternatively, if API functions like `commit_changes` support `author_name` and `author_email` parameters, provide them explicitly.

These examples are conceptual and aim to illustrate the intended use of the `git_operations` module API once implemented. Actual function names, parameters, and return types should be confirmed from `API_SPECIFICATION.md` and the module's source code. 