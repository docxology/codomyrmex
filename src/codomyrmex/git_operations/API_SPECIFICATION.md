# git_operations API Specification

**Version**: v1.0.5 | **Status**: Active | **Last Updated**: March 2026

## Overview

The git_operations module provides comprehensive Git workflow automation, repository management, and version control operations. It exposes both CLI and programmatic APIs for interacting with Git repositories.

## Core API

### Repository Operations

```python
from codomyrmex.git_operations import (
    check_git_availability,
    is_git_repository,
    initialize_git_repository,
    clone_repository,
)

# Check git is installed
available = check_git_availability()  # -> bool

# Check if path is a git repo
is_repo = is_git_repository("/path/to/dir")  # -> bool

# Initialize a new repository
initialized = initialize_git_repository("/path/to/new/repo", initial_commit=True)  # -> bool

# Clone a repository
cloned = clone_repository(
    url="https://github.com/example/repo.git",
    destination="/path/to/local",
    branch="main",
)  # -> bool
```

### File and Commit Operations

```python
from codomyrmex.git_operations import (
    add_files,
    commit_changes,
    get_status,
    get_diff,
    reset_changes,
)

# Stage files
add_files(["file1.py", "file2.py"], repository_path="/path/to/repo")  # -> bool

# Create commit
commit_hash = commit_changes(
    message="Add new feature",
    repository_path="/path/to/repo",
    author_name="Developer",
    author_email="dev@example.com",
    stage_all=True,
)  # -> str | None

# Get repository status
status = get_status(repository_path="/path/to/repo")  # -> dict

# Get diff
diff = get_diff(target="HEAD", repository_path="/path/to/repo", cached=False)  # -> str

# Reset changes
reset_changes(mode="mixed", target="HEAD", repository_path="/path/to/repo")  # -> bool
```

### Branch Operations

```python
from codomyrmex.git_operations import (
    create_branch,
    switch_branch,
    get_current_branch,
    list_branches,
    delete_branch,
    merge_branch,
)

# Create branch
create_branch("feature/new-feature", repository_path="/path/to/repo")  # -> bool

# Switch to branch
switch_branch("feature/new-feature", repository_path="/path/to/repo")  # -> bool

# Get current branch
branch = get_current_branch(repository_path="/path/to/repo")  # -> str | None

# List branches
branches = list_branches(repository_path="/path/to/repo")  # -> list[str]

# Delete branch
delete_branch("feature/old", repository_path="/path/to/repo", force=False)  # -> bool

# Merge branch
merge_branch(
    source_branch="feature/new-feature",
    target_branch="main",
    repository_path="/path/to/repo",
    strategy=None,
)  # -> bool
```

### Remote Operations

```python
from codomyrmex.git_operations import (
    push_changes,
    pull_changes,
    fetch_changes,
    add_remote,
)

# Add remote
add_remote("upstream", "https://github.com/upstream/repo.git", repository_path="/path/to/repo")  # -> bool

# Fetch updates
fetch_changes(remote="origin", branch=None, repository_path="/path/to/repo", prune=False)  # -> bool

# Pull changes
pull_changes(remote="origin", branch="main", repository_path="/path/to/repo")  # -> bool

# Push changes
push_changes(remote="origin", branch="feature-branch", repository_path="/path/to/repo")  # -> bool
```

### Repository Management

```python
from codomyrmex.git_operations import (
    Repository,
    RepositoryManager,
    RepositoryType,
    RepositoryMetadataManager,
    RepositoryMetadata,
    CloneStatus,
)

# Repository types
repo_type = RepositoryType.OWN  # OWN, FORK, USE

# Repository manager
manager = RepositoryManager()
repo = manager.get_repository("/path/to/repo")

# Metadata
metadata_mgr = RepositoryMetadataManager(repo)
```

## Merge Conflict Resolution

```python
from codomyrmex.git_operations.merge_resolver import MergeResolver, ResolutionStrategy

resolver = MergeResolver(repo_path=Path("/path/to/repo"))

# Detect all conflicts
report = resolver.detect_conflicts()
print(report.files_affected)
print(report.conflicts)

# Resolve a specific file using a strategy
resolver.resolve_file("src/main.py", ResolutionStrategy.OURS)

# Auto-resolve trivial conflicts (whitespace-only differences)
resolved_count = resolver.auto_resolve_trivial()
```

Available strategies: `ResolutionStrategy.OURS`, `ResolutionStrategy.THEIRS`, `ResolutionStrategy.UNION`, `ResolutionStrategy.MANUAL`.

## PR Automation

```python
from codomyrmex.git_operations.pr_builder import PRBuilder, PRSpec, FileChange

builder = PRBuilder()
pr = builder.create(
    changes=[FileChange("src/new.py", "def hello(): pass")],
    description="Add hello function",
)
print(pr.branch)    # "auto/add-hello-function"
print(pr.to_dict())
```

`PRBuilder.create()` accepts:
- `changes` -- list of `FileChange` objects (path, content, action)
- `description` -- PR description
- `title` -- PR title (auto-generated from changes if empty)
- `labels` -- list of label strings
- `test_results` -- dict of test pass/fail summary

## Error Handling

```python
from codomyrmex.exceptions import GitOperationError, RepositoryError

try:
    clone_repository("https://github.com/example/repo.git", "/path/to/local")
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
