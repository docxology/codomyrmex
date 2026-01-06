# Git Operations - Usage Examples

This document provides practical usage examples for the `git_operations` module. These examples showcase how to use the `GitManager` API to automate common Git tasks programmatically within the Codomyrmex ecosystem.

## Prerequisites

- Ensure the `git` command-line tool is installed and in your PATH.
- Your Python environment should be set up as per `environment_setup/README.md`.
- For operations involving remotes, ensure Git authentication (SSH keys, credential manager) is configured.

```python
import os
from codomyrmex.git_operations.git_manager import (
    get_status,
    get_current_branch,
    create_branch,
    commit_changes,
    push_changes,
    get_commit_history
)

# Set the path to your repository
repo_path = os.getcwd() 
```

## Example 1: Checking Repository Status

This example shows how to retrieve and display the status of a Git repository, including untracked, modified, and staged files.

```python
try:
    status = get_status(repository_path=repo_path)
    print(f"Current branch: {status['current_branch']}")
    
    if status['is_dirty']:
        print("Repository has uncommitted changes:")
        if status['untracked']:
            print(f"  Untracked files: {status['untracked']}")
        if status['modified']:
            print(f"  Modified files: {status['modified']}")
        if status['staged']:
            print(f"  Staged files: {status['staged']}")
    else:
        print("Repository is clean.")
        
    print(f"Ahead by: {status['ahead_by']}, Behind by: {status['behind_by']}")
except Exception as e:
    print(f"Error getting status: {e}")
```

## Example 2: Feature Branch Workflow

This example demonstrates creating a new feature branch, staging changes, and committing them.

```python
branch_name = "feature/new-ai-model"
commit_msg = "feat: integrate new AI model adaptation logic"

try:
    # Create and switch to a new branch
    if create_branch(branch_name=branch_name, repository_path=repo_path):
        print(f"Created and switched to branch: {branch_name}")
        
        # ... perform code changes ...
        
        # Commit all changes (staging them automatically)
        result = commit_changes(
            message=commit_msg,
            repository_path=repo_path,
            stage_all=True
        )
        
        if result:
            print(f"Committed changes. Commit hash: {result}")
        else:
            print("No changes to commit.")
except Exception as e:
    print(f"Error in branch workflow: {e}")
```

## Example 3: Viewing Commit History

This example shows how to retrieve the recent commit history for the current branch.

```python
try:
    history = get_commit_history(limit=5, repository_path=repo_path)
    print("Recent Commits:")
    for commit in history:
        print(f"  - {commit['hash'][:7]} | {commit['date']} | {commit['author']}")
        print(f"    {commit['message']}")
except Exception as e:
    print(f"Error retrieving history: {e}")
```

## Common Pitfalls & Troubleshooting

- **Issue**: **Git Not Available**
  - **Solution**: The module requires the Git CLI to be installed. Run `check_git_availability()` to verify your environment.

- **Issue**: **Dirty Working Directory**
  - **Solution**: Operations like switching branches or merging may fail if you have uncommitted changes. Use `get_status()` to check the state and `stash_changes()` if needed.

- **Issue**: **Authentication Failures with Remotes**
  - **Solution**: `push_changes()` and `pull_changes()` depend on your system's Git authentication (e.g., SSH keys or Credential Manager). Ensure you can push/pull manually before automating with this module.

- **Issue**: **Author Information Missing**
  - **Solution**: If `commit_changes()` fails due to missing user name/email, ensure they are set in your global Git config or pass `author_name` and `author_email` explicitly to the function.