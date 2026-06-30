# Git Operations - Usage Examples

This document provides practical usage examples for the `git_operations` module, demonstrating how to use the API to automate common Git tasks.

## Prerequisites

```python
from codomyrmex.git_operations import (
    check_git_availability,
    is_git_repository,
    initialize_git_repository,
    create_branch,
    switch_branch,
    get_current_branch,
    add_files,
    commit_changes,
    push_changes,
    pull_changes,
    get_status,
    get_commit_history,
    merge_branch,
    create_tag,
    list_tags,
    stash_changes,
    apply_stash,
    list_stashes
)
```

## Example 1: Basic Repository Setup

```python
# Check if Git is available
if not check_git_availability():
    print("Git is not installed or not in PATH")
    exit(1)

# Initialize a new repository
repo_path = "/path/to/new/project"
if initialize_git_repository(repo_path, initial_commit=True):
    print(f"Repository initialized at {repo_path}")
else:
    print("Failed to initialize repository")

# Verify it's a Git repository
if is_git_repository(repo_path):
    print("Repository verified")
```

## Example 2: Feature Branch Workflow

```python
# Start from main branch
switch_branch("main")

# Create and switch to feature branch
feature_name = "feature/user-authentication"
if create_branch(feature_name):
    print(f"Created and switched to {feature_name}")

    # Make changes and commit
    add_files(["auth.py", "test_auth.py"])
    if commit_changes("feat(auth): Add user authentication system"):
        print("Changes committed")

    # Push to remote
    if push_changes(branch=feature_name):
        print(f"Pushed {feature_name} to remote")
```

## Example 3: Checking Repository Status

```python
# Get current status
status = get_status()

print(f"Current branch: {status.get('branch')}")
print(f"Has uncommitted changes: {status.get('is_dirty')}")

if status.get('untracked_files'):
    print(f"Untracked files: {status['untracked_files']}")

if status.get('modified_files'):
    print(f"Modified files: {status['modified_files']}")

if status.get('staged_files'):
    print(f"Staged files: {status['staged_files']}")

# Check if ahead/behind remote
ahead = status.get('ahead_by', 0)
behind = status.get('behind_by', 0)
if ahead > 0:
    print(f"Ahead of remote by {ahead} commits")
if behind > 0:
    print(f"Behind remote by {behind} commits")
```

## Example 4: Viewing Commit History

```python
# Get recent commits
commits = get_commit_history(max_count=10)

for commit in commits:
    print(f"{commit['short_sha']} - {commit['message']}")
    print(f"  Author: {commit['author']} ({commit['email']})")
    print(f"  Date: {commit['date']}")
    print()

# Get commits for specific branch
feature_commits = get_commit_history(branch="feature/new-feature", max_count=5)
```

## Example 5: Merging Feature Branch

```python
# Switch to main branch
switch_branch("main")

# Pull latest changes
pull_changes()

# Merge feature branch
feature_branch = "feature/user-authentication"
if merge_branch(feature_branch, "main"):
    print(f"Successfully merged {feature_branch} into main")

    # Push merged changes
    push_changes(branch="main")
else:
    print("Merge failed - check for conflicts")
```

## Example 6: Stashing Changes

```python
# Stash current changes
if stash_changes(message="WIP: In-progress feature"):
    print("Changes stashed")

    # Switch branches
    switch_branch("main")

    # Do work on main
    # ...

    # Switch back and apply stash
    switch_branch("feature/in-progress")
    if apply_stash():
        print("Stash applied successfully")

# List all stashes
stashes = list_stashes()
for stash in stashes:
    print(f"Stash: {stash['ref']} - {stash['message']}")
```

## Example 7: Tagging Releases

```python
# Create a release tag
version = "v1.2.0"
if create_tag(
    tag_name=version,
    message=f"Release {version}: Major features and improvements"
):
    print(f"Tag {version} created")

    # Push tag to remote
    push_changes(branch=version)  # Push tag as branch reference

# List all tags
tags = list_tags()
print(f"Available tags: {tags}")
```

## Example 8: Working with Multiple Branches

```python
# Get current branch
current = get_current_branch()
print(f"Currently on: {current}")

# Create multiple feature branches
branches = [
    "feature/auth",
    "feature/database",
    "feature/api"
]

for branch in branches:
    if create_branch(branch):
        print(f"Created {branch}")
        # Work on branch...
        # Switch back to main
        switch_branch("main")
```

## Example 9: Automated Commit Workflow

```python
import os
from pathlib import Path

def auto_commit_changes(repo_path: str, message: str):
    """Automatically stage and commit all changes."""
    # Get all modified and untracked files
    status = get_status(repo_path)

    files_to_add = []
    files_to_add.extend(status.get('modified_files', []))
    files_to_add.extend(status.get('untracked_files', []))

    if files_to_add:
        # Add all files
        if add_files(files_to_add, repo_path):
            # Commit
            if commit_changes(message, repo_path):
                print(f"Committed {len(files_to_add)} files")
                return True

    print("No changes to commit")
    return False

# Usage
auto_commit_changes(".", "chore: Auto-commit changes")
```

## Example 10: Clone and Setup Repository

```python
# Clone a repository
repo_url = "https://github.com/user/repo.git"
destination = "/path/to/clone"

if clone_repository(repo_url, destination):
    print(f"Repository cloned to {destination}")

    # Switch to specific branch
    switch_branch("develop", repository_path=destination)

    # Get status
    status = get_status(destination)
    print(f"Current branch: {status['branch']}")
```

## Example 11: Rebase Workflow

```python
# Start on feature branch
switch_branch("feature/new-feature")

# Rebase onto latest main
if rebase_branch("feature/new-feature", "main"):
    print("Rebase successful")

    # Push rebased branch (may need force push)
    push_changes(branch="feature/new-feature")
else:
    print("Rebase failed - manual resolution may be needed")
```

## Example 12: Viewing Diffs

```python
# Get diff of working directory changes
diff = get_diff()
print("Working directory diff:")
print(diff)

# Get diff of staged changes
staged_diff = get_diff(staged=True)
print("
Staged changes diff:")
print(staged_diff)
```

## Example 13: Resetting Changes

```python
# Reset all changes (mixed - keeps working directory)
if reset_changes(mode="mixed"):
    print("Reset successful - changes unstaged but preserved")

# Reset to HEAD (hard - discards all changes)
# WARNING: This is destructive
if reset_changes(mode="hard"):
    print("Hard reset - all uncommitted changes discarded")
```

## Example 14: Complete Feature Development Workflow

```python
def complete_feature_workflow(feature_name: str, files: list[str]):
    """Complete workflow from branch creation to push."""
    # 1. Ensure on main and up to date
    switch_branch("main")
    pull_changes()

    # 2. Create feature branch
    branch_name = f"feature/{feature_name}"
    if not create_branch(branch_name):
        print(f"Failed to create branch {branch_name}")
        return False

    # 3. Add and commit files
    if not add_files(files):
        print("Failed to stage files")
        return False

    commit_msg = f"feat: Add {feature_name}"
    if not commit_changes(commit_msg):
        print("Failed to commit changes")
        return False

    # 4. Push to remote
    if not push_changes(branch=branch_name):
        print("Failed to push branch")
        return False

    print(f"Feature branch {branch_name} created and pushed")
    print(f"Create PR from {branch_name} to main")
    return True

# Usage
complete_feature_workflow(
    "user-profile",
    ["user_profile.py", "test_user_profile.py", "user_profile.md"]
)
```

## Error Handling Best Practices

```python
# Always check return values
if not check_git_availability():
    logger.error("Git not available")
    return

# Check repository state before operations
if not is_git_repository():
    logger.error("Not a Git repository")
    return

# Verify branch exists before switching
status = get_status()
if status['branch'] != target_branch:
    if not switch_branch(target_branch):
        logger.error(f"Failed to switch to {target_branch}")
        return

# Check for uncommitted changes before destructive operations
status = get_status()
if status['is_dirty']:
    logger.warning("Repository has uncommitted changes")
    # Optionally stash or commit before proceeding
    stash_changes()
```

## Integration with Other Modules

```python
# With logging_monitoring
from codomyrmex.logging_monitoring import get_logger
logger = get_logger(__name__)

logger.info("Starting Git operations")
if create_branch("feature/new"):
    logger.info("Branch created successfully")
else:
    logger.error("Failed to create branch")

# With visualization
from codomyrmex.git_operations.visualization_integration import (
    create_git_analysis_report
)

create_git_analysis_report(
    repository_path=".",
    output_dir="./git_analysis"
)
```

For more detailed function signatures and parameters, see [API_SPECIFICATION.md](./API_SPECIFICATION.md).

## Navigation Links

- **Parent**: [Project Overview](../README.md)
- **Module Index**: [All Agents](../../AGENTS.md)
- **Documentation**: [Reference Guides](../../README.md)
- **Home**: [Root README](../../../README.md)
