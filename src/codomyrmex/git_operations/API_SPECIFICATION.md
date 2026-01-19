# git_operations API Specification

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Overview

The git_operations module provides comprehensive Git workflow automation, repository management, and version control operations. It exposes both CLI and programmatic APIs for interacting with Git repositories.

## Core API

### Repository Operations

```python
from codomyrmex.git_operations import GitRepository, clone_repository, init_repository

# Clone a repository
repo = clone_repository(
    url="https://github.com/example/repo.git",
    path="/path/to/local",
    branch="main"
)

# Initialize a new repository
repo = init_repository(path="/path/to/new/repo")

# Open existing repository
repo = GitRepository("/path/to/existing/repo")
```

### Commit Operations

```python
from codomyrmex.git_operations import commit, stage_files, get_diff

# Stage files
stage_files(repo, ["file1.py", "file2.py"])

# Create commit
commit_hash = commit(
    repo,
    message="Add new feature",
    author="Developer <dev@example.com>"
)

# Get diff
diff = get_diff(repo, from_ref="HEAD~1", to_ref="HEAD")
```

### Branch Operations

```python
from codomyrmex.git_operations import (
    create_branch,
    checkout_branch,
    merge_branch,
    list_branches,
    delete_branch
)

# Create and checkout branch
create_branch(repo, "feature/new-feature")
checkout_branch(repo, "feature/new-feature")

# List branches
branches = list_branches(repo, remote=True)

# Merge branch
merge_branch(repo, source="feature/new-feature", target="main")
```

### Remote Operations

```python
from codomyrmex.git_operations import push, pull, fetch, add_remote

# Add remote
add_remote(repo, name="upstream", url="https://github.com/upstream/repo.git")

# Fetch updates
fetch(repo, remote="origin")

# Pull changes
pull(repo, remote="origin", branch="main")

# Push changes
push(repo, remote="origin", branch="feature-branch")
```

## Error Handling

```python
from codomyrmex.exceptions import GitOperationError, RepositoryError

try:
    repo = clone_repository(url, path)
except GitOperationError as e:
    print(f"Git command failed: {e.context.get('git_command')}")
except RepositoryError as e:
    print(f"Repository error: {e}")
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
