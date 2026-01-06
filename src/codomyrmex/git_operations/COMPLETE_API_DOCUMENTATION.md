# Git Operations - Complete API Documentation

## Overview

The Git Operations module provides a comprehensive, production-ready interface for all Git operations within the Codomyrmex ecosystem. This module supports complete fractal Git workflows with 22 operations covering all aspects of Git repository management.

## Quick Start

```python
from codomyrmex.git_operations import (
    check_git_availability, initialize_git_repository, 
    create_branch, add_files, commit_changes, merge_branch
)

# Check if Git is available
if check_git_availability():
    # Initialize a new repository
    initialize_git_repository("/path/to/repo", initial_commit=True)
    
    # Create and work on a feature branch
    create_branch("feature/new-feature", "/path/to/repo")
    add_files(["new_file.py"], "/path/to/repo")
    commit_changes("Add new feature", "/path/to/repo")
    
    # Merge back to main
    merge_branch("feature/new-feature", "main", "/path/to/repo")
```

---

## Core Operations

### check_git_availability()

**Description**: Verifies that Git is installed and accessible on the system.

**Parameters**: None

**Returns**: `bool` - True if Git is available, False otherwise

**Example**:
```python
from codomyrmex.git_operations import check_git_availability

if check_git_availability():
    print("Git is available and ready to use")
else:
    print("Git is not installed or not in PATH")
```

**Error Handling**: Returns False for any Git-related errors or if Git is not found.

---

### is_git_repository(path=None)

**Description**: Checks if the specified path (or current directory) is a Git repository.

**Parameters**:
- `path` (str, optional): Path to check. Defaults to current working directory.

**Returns**: `bool` - True if path is a Git repository, False otherwise

**Example**:
```python
from codomyrmex.git_operations import is_git_repository

# Check current directory
if is_git_repository():
    print("Current directory is a Git repository")

# Check specific path
if is_git_repository("/path/to/project"):
    print("Project directory is a Git repository")
else:
    print("Not a Git repository")
```

**Error Handling**: Returns False for invalid paths or non-Git directories.

---

### initialize_git_repository(path, initial_commit=True)

**Description**: Creates a new Git repository at the specified path with optional initial commit.

**Parameters**:
- `path` (str): Directory path where the repository will be created
- `initial_commit` (bool, optional): Whether to create an initial commit with README.md. Defaults to True.

**Returns**: `bool` - True if repository was created successfully, False otherwise

**Example**:
```python
from codomyrmex.git_operations import initialize_git_repository

# Initialize with initial commit
success = initialize_git_repository("/path/to/new/repo")
if success:
    print("Repository initialized with initial commit")

# Initialize without initial commit
success = initialize_git_repository("/path/to/empty/repo", initial_commit=False)
if success:
    print("Empty repository initialized")
```

**Error Handling**: Returns False if directory creation fails or Git initialization fails.

---

### clone_repository(url, destination, branch=None)

**Description**: Clones a remote Git repository to the specified local destination.

**Parameters**:
- `url` (str): Remote repository URL to clone
- `destination` (str): Local directory path for the cloned repository
- `branch` (str, optional): Specific branch to clone. Defaults to repository default.

**Returns**: `bool` - True if repository was cloned successfully, False otherwise

**Example**:
```python
from codomyrmex.git_operations import clone_repository

# Clone entire repository
success = clone_repository(
    "https://github.com/user/repo.git", 
    "/local/path/repo"
)

# Clone specific branch
success = clone_repository(
    "https://github.com/user/repo.git", 
    "/local/path/repo",
    branch="develop"
)
```

**Error Handling**: Returns False for network errors, invalid URLs, or permission issues.

---

## Branch Operations

### create_branch(branch_name, repository_path=None)

**Description**: Creates a new branch and switches to it.

**Parameters**:
- `branch_name` (str): Name of the new branch to create
- `repository_path` (str, optional): Path to Git repository. Defaults to current directory.

**Returns**: `bool` - True if branch was created successfully, False otherwise

**Example**:
```python
from codomyrmex.git_operations import create_branch

# Create feature branch
success = create_branch("feature/user-authentication")
if success:
    print("Feature branch created and checked out")

# Create branch in specific repository
success = create_branch("hotfix/critical-bug", "/path/to/repo")
```

**Error Handling**: Returns False if branch already exists or repository is invalid.

---

### switch_branch(branch_name, repository_path=None)

**Description**: Switches to an existing branch.

**Parameters**:
- `branch_name` (str): Name of the branch to switch to
- `repository_path` (str, optional): Path to Git repository. Defaults to current directory.

**Returns**: `bool` - True if branch switch was successful, False otherwise

**Example**:
```python
from codomyrmex.git_operations import switch_branch

# Switch to main branch
success = switch_branch("main")
if success:
    print("Switched to main branch")

# Switch to feature branch
success = switch_branch("feature/new-feature", "/path/to/repo")
```

**Error Handling**: Returns False if branch doesn't exist or has uncommitted changes blocking switch.

---

### get_current_branch(repository_path=None)

**Description**: Gets the name of the currently active branch.

**Parameters**:
- `repository_path` (str, optional): Path to Git repository. Defaults to current directory.

**Returns**: `str | None` - Name of current branch, or None if error

**Example**:
```python
from codomyrmex.git_operations import get_current_branch

current = get_current_branch()
if current:
    print(f"Currently on branch: {current}")
else:
    print("Could not determine current branch")

# Check specific repository
current = get_current_branch("/path/to/repo")
```

**Error Handling**: Returns None for invalid repositories or Git errors.

---

### merge_branch(source_branch, target_branch=None, repository_path=None, strategy=None)

**Description**: Merges a source branch into the target branch.

**Parameters**:
- `source_branch` (str): Name of the branch to merge from
- `target_branch` (str, optional): Name of the branch to merge into. Defaults to current branch.
- `repository_path` (str, optional): Path to Git repository. Defaults to current directory.
- `strategy` (str, optional): Merge strategy (e.g., 'recursive', 'ours', 'theirs'). Defaults to Git default.

**Returns**: `bool` - True if merge was successful, False otherwise

**Example**:
```python
from codomyrmex.git_operations import merge_branch

# Merge feature branch into current branch
success = merge_branch("feature/new-feature")
if success:
    print("Feature branch merged successfully")

# Merge with specific target and strategy
success = merge_branch(
    "feature/complex-feature", 
    "main", 
    "/path/to/repo",
    strategy="recursive"
)
```

**Error Handling**: Returns False for merge conflicts, non-existent branches, or Git errors.

---

### rebase_branch(target_branch, repository_path=None, interactive=False)

**Description**: Rebases the current branch onto the target branch.

**Parameters**:
- `target_branch` (str): Name of the branch to rebase onto
- `repository_path` (str, optional): Path to Git repository. Defaults to current directory.
- `interactive` (bool, optional): Whether to perform interactive rebase. Defaults to False.

**Returns**: `bool` - True if rebase was successful, False otherwise

**Example**:
```python
from codomyrmex.git_operations import rebase_branch

# Standard rebase onto main
success = rebase_branch("main")
if success:
    print("Rebased onto main successfully")

# Interactive rebase
success = rebase_branch("develop", interactive=True)
```

**Error Handling**: Returns False for rebase conflicts, non-existent branches, or Git errors.

---

## File Operations

### add_files(file_paths, repository_path=None)

**Description**: Stages files for the next commit.

**Parameters**:
- `file_paths` (List[str]): List of file paths to stage
- `repository_path` (str, optional): Path to Git repository. Defaults to current directory.

**Returns**: `bool` - True if files were staged successfully, False otherwise

**Example**:
```python
from codomyrmex.git_operations import add_files

# Add single file
success = add_files(["new_feature.py"])

# Add multiple files
success = add_files([
    "src/module.py", 
    "tests/test_module.py", 
    "docs/api.md"
])

# Add files in specific repository
success = add_files(["config.json"], "/path/to/repo")
```

**Error Handling**: Returns False for non-existent files or Git errors.

---

### commit_changes(message, repository_path=None)

**Description**: Commits staged changes with the specified message.

**Parameters**:
- `message` (str): Commit message
- `repository_path` (str, optional): Path to Git repository. Defaults to current directory.

**Returns**: `bool` - True if commit was successful, False otherwise

**Example**:
```python
from codomyrmex.git_operations import commit_changes

# Simple commit
success = commit_changes("Add new user authentication feature")
if success:
    print("Changes committed successfully")

# Commit in specific repository
success = commit_changes(
    "Fix critical security vulnerability", 
    "/path/to/repo"
)
```

**Error Handling**: Returns False if no changes are staged or Git errors occur.

---

### get_status(repository_path=None)

**Description**: Gets the current status of the Git repository.

**Parameters**:
- `repository_path` (str, optional): Path to Git repository. Defaults to current directory.

**Returns**: `Dict[str, Any]` - Dictionary containing repository status information

**Return Structure**:
```python
{
    "modified": ["file1.py", "file2.py"],      # Modified files
    "added": ["new_file.py"],                  # Staged new files
    "deleted": ["old_file.py"],                # Deleted files
    "renamed": ["old.py -> new.py"],           # Renamed files
    "untracked": ["temp.txt"],                 # Untracked files
    "clean": False                             # True if working tree is clean
}
```

**Example**:
```python
from codomyrmex.git_operations import get_status

status = get_status()
if status.get("clean"):
    print("Working tree is clean")
else:
    print(f"Modified files: {status['modified']}")
    print(f"Untracked files: {status['untracked']}")

# Check specific repository
status = get_status("/path/to/repo")
```

**Error Handling**: Returns dictionary with "error" key for invalid repositories.

---

### get_diff(file_path=None, staged=False, repository_path=None)

**Description**: Gets the diff of changes in the repository.

**Parameters**:
- `file_path` (str, optional): Specific file to get diff for. Defaults to all files.
- `staged` (bool, optional): Whether to get diff of staged changes. Defaults to False (working tree).
- `repository_path` (str, optional): Path to Git repository. Defaults to current directory.

**Returns**: `str` - Diff output as string

**Example**:
```python
from codomyrmex.git_operations import get_diff

# Get diff of all working tree changes
diff = get_diff()
if diff:
    print("Working tree changes:")
    print(diff)

# Get diff of staged changes
staged_diff = get_diff(staged=True)

# Get diff of specific file
file_diff = get_diff("src/module.py")

# Get diff in specific repository
diff = get_diff(repository_path="/path/to/repo")
```

**Error Handling**: Returns empty string for invalid repositories or Git errors.

---

### reset_changes(mode="mixed", target="HEAD", repository_path=None)

**Description**: Resets the repository to a specific state.

**Parameters**:
- `mode` (str, optional): Reset mode ('soft', 'mixed', 'hard'). Defaults to 'mixed'.
- `target` (str, optional): Target commit/branch to reset to. Defaults to 'HEAD'.
- `repository_path` (str, optional): Path to Git repository. Defaults to current directory.

**Returns**: `bool` - True if reset was successful, False otherwise

**Reset Modes**:
- `soft`: Keeps changes staged
- `mixed`: Unstages changes but keeps them in working tree
- `hard`: Discards all changes (DESTRUCTIVE)

**Example**:
```python
from codomyrmex.git_operations import reset_changes

# Soft reset (keep changes staged)
success = reset_changes("soft", "HEAD~1")

# Mixed reset (unstage changes)
success = reset_changes("mixed", "HEAD")

# Hard reset (CAUTION: destroys changes)
success = reset_changes("hard", "HEAD~2")

# Reset in specific repository
success = reset_changes("mixed", "main", "/path/to/repo")
```

**Error Handling**: Returns False for invalid modes, targets, or Git errors.

---

## Remote Operations

### push_changes(remote="origin", branch=None, repository_path=None)

**Description**: Pushes committed changes to a remote repository.

**Parameters**:
- `remote` (str, optional): Name of the remote. Defaults to 'origin'.
- `branch` (str, optional): Name of the branch to push. Defaults to current branch.
- `repository_path` (str, optional): Path to Git repository. Defaults to current directory.

**Returns**: `bool` - True if push was successful, False otherwise

**Example**:
```python
from codomyrmex.git_operations import push_changes

# Push current branch to origin
success = push_changes()
if success:
    print("Changes pushed successfully")

# Push specific branch to specific remote
success = push_changes("upstream", "feature/new-feature")

# Push in specific repository
success = push_changes("origin", "main", "/path/to/repo")
```

**Error Handling**: Returns False for network errors, authentication failures, or Git errors.

---

### pull_changes(remote="origin", branch=None, repository_path=None)

**Description**: Pulls changes from a remote repository.

**Parameters**:
- `remote` (str, optional): Name of the remote. Defaults to 'origin'.
- `branch` (str, optional): Name of the branch to pull. Defaults to current branch.
- `repository_path` (str, optional): Path to Git repository. Defaults to current directory.

**Returns**: `bool` - True if pull was successful, False otherwise

**Example**:
```python
from codomyrmex.git_operations import pull_changes

# Pull current branch from origin
success = pull_changes()
if success:
    print("Changes pulled successfully")

# Pull specific branch from specific remote
success = pull_changes("upstream", "develop")

# Pull in specific repository
success = pull_changes("origin", "main", "/path/to/repo")
```

**Error Handling**: Returns False for network errors, merge conflicts, or Git errors.

---

## History & Information

### get_commit_history(limit=10, repository_path=None)

**Description**: Gets the commit history of the repository.

**Parameters**:
- `limit` (int, optional): Maximum number of commits to retrieve. Defaults to 10.
- `repository_path` (str, optional): Path to Git repository. Defaults to current directory.

**Returns**: `List[Dict[str, str]]` - List of commit information dictionaries

**Commit Structure**:
```python
{
    "hash": "a1b2c3d4e5f6...",           # Commit hash
    "author_name": "John Doe",           # Author name
    "author_email": "john@example.com",  # Author email
    "date": "Mon Jan 1 12:00:00 2024",   # Commit date
    "message": "Add new feature"         # Commit message
}
```

**Example**:
```python
from codomyrmex.git_operations import get_commit_history

# Get last 10 commits
commits = get_commit_history()
for commit in commits:
    print(f"{commit['hash'][:8]} - {commit['message']}")
    print(f"Author: {commit['author_name']} ({commit['date']})")

# Get last 5 commits
recent_commits = get_commit_history(limit=5)

# Get commits from specific repository
commits = get_commit_history(20, "/path/to/repo")
```

**Error Handling**: Returns empty list for invalid repositories or Git errors.

---

## Tag Operations

### create_tag(tag_name, message=None, repository_path=None)

**Description**: Creates a Git tag at the current commit.

**Parameters**:
- `tag_name` (str): Name of the tag to create
- `message` (str, optional): Tag message for annotated tags. If None, creates lightweight tag.
- `repository_path` (str, optional): Path to Git repository. Defaults to current directory.

**Returns**: `bool` - True if tag was created successfully, False otherwise

**Example**:
```python
from codomyrmex.git_operations import create_tag

# Create lightweight tag
success = create_tag("v1.0.0")
if success:
    print("Lightweight tag created")

# Create annotated tag
success = create_tag("v1.1.0", "Release version 1.1.0 with new features")
if success:
    print("Annotated tag created")

# Create tag in specific repository
success = create_tag("hotfix-v1.0.1", "Critical bug fix", "/path/to/repo")
```

**Error Handling**: Returns False if tag already exists or Git errors occur.

---

### list_tags(repository_path=None)

**Description**: Lists all tags in the repository.

**Parameters**:
- `repository_path` (str, optional): Path to Git repository. Defaults to current directory.

**Returns**: `List[str]` - List of tag names

**Example**:
```python
from codomyrmex.git_operations import list_tags

# List all tags
tags = list_tags()
if tags:
    print("Available tags:")
    for tag in tags:
        print(f"  - {tag}")
else:
    print("No tags found")

# List tags in specific repository
tags = list_tags("/path/to/repo")
```

**Error Handling**: Returns empty list for invalid repositories or Git errors.

---

## Stash Operations

### stash_changes(message=None, repository_path=None)

**Description**: Stashes current uncommitted changes.

**Parameters**:
- `message` (str, optional): Stash message for identification. Defaults to Git default.
- `repository_path` (str, optional): Path to Git repository. Defaults to current directory.

**Returns**: `bool` - True if stash was created successfully, False otherwise

**Example**:
```python
from codomyrmex.git_operations import stash_changes

# Stash with default message
success = stash_changes()
if success:
    print("Changes stashed")

# Stash with custom message
success = stash_changes("Work in progress on user authentication")

# Stash in specific repository
success = stash_changes("Temporary changes", "/path/to/repo")
```

**Error Handling**: Returns False if no changes to stash or Git errors occur.

---

### apply_stash(stash_ref=None, repository_path=None)

**Description**: Applies stashed changes back to the working tree.

**Parameters**:
- `stash_ref` (str, optional): Specific stash reference (e.g., 'stash@{0}'). Defaults to most recent.
- `repository_path` (str, optional): Path to Git repository. Defaults to current directory.

**Returns**: `bool` - True if stash was applied successfully, False otherwise

**Example**:
```python
from codomyrmex.git_operations import apply_stash

# Apply most recent stash
success = apply_stash()
if success:
    print("Stash applied successfully")

# Apply specific stash
success = apply_stash("stash@{1}")

# Apply stash in specific repository
success = apply_stash("stash@{0}", "/path/to/repo")
```

**Error Handling**: Returns False if no stashes exist, conflicts occur, or Git errors.

---

### list_stashes(repository_path=None)

**Description**: Lists all stashes in the repository.

**Parameters**:
- `repository_path` (str, optional): Path to Git repository. Defaults to current directory.

**Returns**: `List[Dict[str, str]]` - List of stash information dictionaries

**Stash Structure**:
```python
{
    "ref": "stash@{0}",                    # Stash reference
    "branch_info": "WIP on main",          # Branch information
    "message": "Custom stash message"      # Stash message
}
```

**Example**:
```python
from codomyrmex.git_operations import list_stashes

# List all stashes
stashes = list_stashes()
if stashes:
    print("Available stashes:")
    for stash in stashes:
        print(f"  {stash['ref']}: {stash['message']}")
else:
    print("No stashes found")

# List stashes in specific repository
stashes = list_stashes("/path/to/repo")
```

**Error Handling**: Returns empty list for invalid repositories or Git errors.

---

## Complete Workflow Examples

### Feature Branch Workflow

```python
from codomyrmex.git_operations import (
    initialize_git_repository, create_branch, add_files, 
    commit_changes, switch_branch, merge_branch, create_tag
)

# Initialize repository
repo_path = "/path/to/project"
initialize_git_repository(repo_path)

# Create feature branch
create_branch("feature/user-auth", repo_path)

# Work on feature
add_files(["auth.py", "tests/test_auth.py"], repo_path)
commit_changes("Implement user authentication", repo_path)

add_files(["auth_middleware.py"], repo_path)
commit_changes("Add authentication middleware", repo_path)

# Switch back to main and merge
switch_branch("main", repo_path)
merge_branch("feature/user-auth", repository_path=repo_path)

# Tag the release
create_tag("v1.0.0", "Release with user authentication", repo_path)
```

### Hotfix Workflow

```python
from codomyrmex.git_operations import (
    create_branch, add_files, commit_changes, 
    switch_branch, merge_branch, create_tag, push_changes
)

repo_path = "/path/to/project"

# Create hotfix branch from main
switch_branch("main", repo_path)
create_branch("hotfix/security-fix", repo_path)

# Apply fix
add_files(["security_patch.py"], repo_path)
commit_changes("Fix critical security vulnerability", repo_path)

# Merge to main
switch_branch("main", repo_path)
merge_branch("hotfix/security-fix", repository_path=repo_path)

# Tag and push
create_tag("v1.0.1", "Security hotfix", repo_path)
push_changes("origin", "main", repo_path)
```

### Stash Workflow

```python
from codomyrmex.git_operations import (
    get_status, stash_changes, switch_branch, 
    apply_stash, list_stashes
)

repo_path = "/path/to/project"

# Check current status
status = get_status(repo_path)
if not status["clean"]:
    # Stash work in progress
    stash_changes("WIP: implementing new feature", repo_path)
    
    # Switch to different branch for urgent fix
    switch_branch("hotfix/urgent", repo_path)
    # ... do urgent work ...
    
    # Switch back and restore work
    switch_branch("feature/new-feature", repo_path)
    apply_stash(repository_path=repo_path)

# List all stashes
stashes = list_stashes(repo_path)
for stash in stashes:
    print(f"Stash: {stash['ref']} - {stash['message']}")
```

---

## Error Handling Best Practices

### Checking Prerequisites

```python
from codomyrmex.git_operations import check_git_availability, is_git_repository

def safe_git_operation(repo_path):
    # Always check Git availability first
    if not check_git_availability():
        raise RuntimeError("Git is not available on this system")
    
    # Verify repository exists
    if not is_git_repository(repo_path):
        raise ValueError(f"Path {repo_path} is not a Git repository")
    
    # Proceed with Git operations
    return True
```

### Comprehensive Error Handling

```python
from codomyrmex.git_operations import commit_changes, get_status

def safe_commit(message, repo_path):
    try:
        # Check if there are changes to commit
        status = get_status(repo_path)
        if status.get("error"):
            print(f"Error getting status: {status['error']}")
            return False
        
        if status.get("clean"):
            print("No changes to commit")
            return True
        
        # Attempt commit
        success = commit_changes(message, repo_path)
        if success:
            print("Commit successful")
            return True
        else:
            print("Commit failed")
            return False
            
    except Exception as e:
        print(f"Unexpected error: {e}")
        return False
```

---

## Performance Considerations

### Batch Operations

```python
from codomyrmex.git_operations import add_files, commit_changes

# Efficient: Add multiple files at once
files_to_add = ["file1.py", "file2.py", "file3.py", "file4.py"]
add_files(files_to_add, repo_path)
commit_changes("Add multiple files", repo_path)

# Inefficient: Adding files one by one
# for file in files_to_add:
#     add_files([file], repo_path)  # Don't do this
```

### Repository Path Optimization

```python
# Efficient: Pass repository path to avoid repeated directory changes
repo_path = "/path/to/repo"
create_branch("feature/optimization", repo_path)
add_files(["optimized.py"], repo_path)
commit_changes("Add optimization", repo_path)

# Less efficient: Relying on current directory
# os.chdir("/path/to/repo")
# create_branch("feature/optimization")  # Works but less explicit
```

---

## Integration with Other Modules

### With Logging

```python
from codomyrmex.git_operations import commit_changes
from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)

def logged_commit(message, repo_path):
    logger.info(f"Attempting to commit: {message}")
    success = commit_changes(message, repo_path)
    if success:
        logger.info("Commit successful")
    else:
        logger.error("Commit failed")
    return success
```

### With Environment Setup

```python
from codomyrmex.git_operations import check_git_availability
from codomyrmex.environment_setup import ensure_dependencies_installed

def setup_git_environment():
    # Ensure basic dependencies
    ensure_dependencies_installed()
    
    # Check Git availability
    if not check_git_availability():
        print("Please install Git to use this module")
        return False
    
    print("Git environment ready")
    return True
```

This comprehensive API documentation covers all 22 Git operations with detailed examples, error handling, and best practices for production use.

## Navigation Links

- **Parent**: [Project Overview](../README.md)
- **Module Index**: [All Agents](../../AGENTS.md)
- **Documentation**: [Reference Guides](../../docs/README.md)
- **Home**: [Root README](../../../README.md)
