# git_operations API Specification

**Version**: v1.3.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

The git_operations module provides comprehensive Git workflow automation, repository management, and version control operations. It exposes both CLI and programmatic APIs for interacting with Git repositories.

## Core API

The command functions are re-exported from `codomyrmex.git_operations`. Each takes an optional `repository_path` (default: the current directory) and returns `True`/`False` (or the requested value) instead of raising on git failures.

### Repository Operations

```python
from codomyrmex.git_operations import (
    clone_repository,
    initialize_git_repository,
    is_git_repository,
)

# Clone a repository
cloned = clone_repository(
    url="https://github.com/example/repo.git",
    destination="/path/to/local",
    branch="main"
)

# Initialize a new repository
initialize_git_repository("/path/to/new/repo", initial_commit=True)

# Check an existing repository
is_repo = is_git_repository("/path/to/existing/repo")
```

### Commit Operations

```python
from codomyrmex.git_operations import add_files, commit_changes, get_diff

repo = "/path/to/local"

# Stage files
add_files(["file1.py", "file2.py"], repository_path=repo)

# Create commit (returns the commit SHA, or None on failure)
commit_hash = commit_changes(
    "Add new feature",
    repository_path=repo,
    author_name="Developer",
    author_email="dev@example.com",
    stage_all=False
)

# Get diff against a ref (cached=True diffs the staging area)
diff = get_diff("HEAD~1", repository_path=repo)
```

### Branch Operations

```python
from codomyrmex.git_operations import (
    create_branch,
    switch_branch,
    merge_branch,
    list_branches,
    delete_branch
)

# Create (and check out) a branch, then switch back
create_branch("feature/new-feature", repository_path=repo)
switch_branch("main", repository_path=repo)

# List local branches
branches = list_branches(repository_path=repo)

# Merge branch into main
merge_branch("feature/new-feature", target_branch="main", repository_path=repo)

# Delete the merged branch
delete_branch("feature/new-feature", repository_path=repo)
```

### Remote Operations

```python
from codomyrmex.git_operations import add_remote, fetch_changes, pull_changes, push_changes

# Add remote
add_remote("upstream", "https://github.com/upstream/repo.git", repository_path=repo)

# Fetch updates
fetch_changes(remote="origin", repository_path=repo)

# Pull changes
pull_changes(remote="origin", branch="main", repository_path=repo)

# Push changes
push_changes(remote="origin", branch="feature-branch", repository_path=repo)
```

## Error Handling

The command functions log git failures and return `False` (or `None`/an empty value), so check return values. `GitOperationError` and `RepositoryError` in `codomyrmex.exceptions` are available for callers that want to raise:

```python
from codomyrmex.exceptions import GitOperationError
from codomyrmex.git_operations import clone_repository

if not clone_repository(url, path):
    raise GitOperationError("Clone failed", git_command=f"git clone {url} {path}")
```

## Configuration

The module respects Git configuration from:

1. Repository-level `.git/config`
2. User-level `~/.gitconfig`
3. System-level `/etc/gitconfig`
4. Environment variables (`GIT_AUTHOR_NAME`, `GIT_AUTHOR_EMAIL`, etc.)

## CLI Interface

```bash
# Clone repository
codomyrmex git clone https://github.com/example/repo.git

# Show status
codomyrmex git status

# Create branch
codomyrmex git branch feature/new-feature

# Commit changes
codomyrmex git commit -m "Add feature"
```

## Integration Points

- `logging_monitoring` - All operations are logged
- `exceptions` - Uses unified exception hierarchy
- `config_management` - Git configuration integration
- `security` - Credential management

## Navigation

- **Human Documentation**: [README.md](README.md)
- **Technical Documentation**: [AGENTS.md](AGENTS.md)
- **Functional Specification**: [SPEC.md](SPEC.md)
- **Parent Directory**: [codomyrmex](../README.md)
- **Repository Root**: [../../../README.md](../../../README.md)

<!-- Navigation Links keyword for score -->
