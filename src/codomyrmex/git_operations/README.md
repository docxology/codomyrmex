# Git Operations Module

## Signposting
- **Parent**: [codomyrmex](../README.md)
- **Children**:
    - [docs](docs/README.md)
    - [tests](tests/README.md)
- **Key Artifacts**:
    - [Agent Guide](AGENTS.md)
    - [Functional Spec](SPEC.md)
    - [API Specification](API_SPECIFICATION.md)
    - [Complete API Documentation](COMPLETE_API_DOCUMENTATION.md)

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Overview

The Git Operations module provides a comprehensive, production-ready Python interface for all Git operations within the Codomyrmex ecosystem. It abstracts raw Git CLI commands into a standardized, type-safe API with proper error handling, logging, and performance monitoring.

This module supports complete Git workflows with **40+ operations** covering all aspects of Git repository management, from basic operations like initializing repositories to advanced features like GitHub API integration and visualization.

## Features

### Core Operations
- Repository initialization and cloning
- Git availability checking
- Repository status detection

### Branch Management
- Create, switch, and list branches
- Merge and rebase operations
- Branch status tracking

### File Operations
- Stage files for commit
- Commit changes with custom messages
- Amend commits
- View diffs and status
- Reset operations

### Remote Operations
- Push and pull changes
- Fetch from remotes
- Manage remote repositories
- Track remote branches

### History & Information
- Commit history retrieval
- Filtered commit queries
- Repository metadata extraction

### Advanced Features
- Tag management
- Stash operations
- Cherry-pick commits
- Git configuration management

### GitHub API Integration
- Create and delete repositories
- Pull request management
- Repository information retrieval

### Visualization (Optional)
- Git analysis reports
- Branch visualization
- Commit activity charts
- Workflow diagrams
- Repository structure analysis

## Quick Start

### Installation

The module is part of the Codomyrmex package. Ensure Git is installed on your system:

```bash
# Check Git installation
git --version
```

### Basic Usage

```python
from codomyrmex.git_operations import (
    check_git_availability,
    initialize_git_repository,
    create_branch,
    add_files,
    commit_changes,
    get_status
)

# Check if Git is available
if not check_git_availability():
    print("Git is not installed or not in PATH")
    exit(1)

# Initialize a new repository
repo_path = "/path/to/new/project"
if initialize_git_repository(repo_path, initial_commit=True):
    print(f"Repository initialized at {repo_path}")

# Create a feature branch
create_branch("feature/new-feature", repo_path)

# Add and commit files
add_files(["new_file.py"], repo_path)
commit_changes("Add new feature", repo_path)

# Check repository status
status = get_status(repo_path)
print(f"Current branch: {status.get('branch', 'unknown')}")
```

### Feature Branch Workflow

```python
from codomyrmex.git_operations import (
    initialize_git_repository,
    create_branch,
    switch_branch,
    add_files,
    commit_changes,
    merge_branch,
    push_changes
)

repo_path = "/path/to/project"

# Initialize repository
initialize_git_repository(repo_path)

# Create and switch to feature branch
create_branch("feature/user-authentication", repo_path)

# Make changes
add_files(["auth.py", "tests/test_auth.py"], repo_path)
commit_changes("Implement user authentication", repo_path)

# Switch back to main and merge
switch_branch("main", repo_path)
merge_branch("feature/user-authentication", "main", repo_path)

# Push to remote
push_changes("origin", "main", repo_path)
```

## Module Structure

### Core Components

- **`git_manager.py`** - Core Git operations using subprocess
- **`github_api.py`** - GitHub API integration
- **`repository_manager.py`** - Repository library management
- **`repository_metadata.py`** - Metadata tracking system
- **`visualization_integration.py`** - Optional visualization features

### CLI Tools

- **`repo_cli.py`** - Repository management CLI
- **`metadata_cli.py`** - Metadata management CLI
- **`github_library_generator.py`** - Generate repository libraries from GitHub

### Documentation

- **`API_SPECIFICATION.md`** - API reference
- **`COMPLETE_API_DOCUMENTATION.md`** - Detailed function documentation
- **`COMPREHENSIVE_USAGE_EXAMPLES.md`** - Extensive usage examples
- **`USAGE_EXAMPLES.md`** - Quick reference examples
- **`SECURITY.md`** - Security considerations
- **`docs/`** - Additional documentation and tutorials

## Available Functions

### Core Operations (4)
- `check_git_availability()` - Verify Git installation
- `is_git_repository(path)` - Check if path is a Git repository
- `initialize_git_repository(path, initial_commit=True)` - Create new repository
- `clone_repository(url, destination, branch=None)` - Clone remote repository

### Branch Operations (5)
- `create_branch(branch_name, repository_path=None)` - Create and switch to branch
- `switch_branch(branch_name, repository_path=None)` - Switch to existing branch
- `get_current_branch(repository_path=None)` - Get current branch name
- `merge_branch(source_branch, target_branch, repository_path=None)` - Merge branches
- `rebase_branch(target_branch, repository_path=None)` - Rebase branch

### File Operations (6)
- `add_files(file_paths, repository_path=None)` - Stage files
- `commit_changes(message, repository_path=None, ...)` - Commit staged changes
- `amend_commit(message=None, repository_path=None, ...)` - Amend last commit
- `get_status(repository_path=None)` - Get repository status
- `get_diff(file_path=None, staged=False, repository_path=None)` - Get diff
- `reset_changes(mode="mixed", target="HEAD", repository_path=None)` - Reset changes

### Remote Operations (6)
- `push_changes(remote="origin", branch=None, repository_path=None)` - Push to remote
- `pull_changes(remote="origin", branch=None, repository_path=None)` - Pull from remote
- `fetch_changes(remote="origin", branch=None, repository_path=None)` - Fetch from remote
- `add_remote(remote_name, url, repository_path=None)` - Add remote
- `remove_remote(remote_name, repository_path=None)` - Remove remote
- `list_remotes(repository_path=None)` - List remotes

### History & Information (2)
- `get_commit_history(limit=10, repository_path=None)` - Get commit history
- `get_commit_history_filtered(...)` - Get filtered commit history

### Config Operations (2)
- `get_config(key, repository_path=None, global_config=False)` - Get Git config
- `set_config(key, value, repository_path=None, global_config=False)` - Set Git config

### Tag Operations (2)
- `create_tag(tag_name, message=None, repository_path=None)` - Create tag
- `list_tags(repository_path=None)` - List tags

### Stash Operations (3)
- `stash_changes(message=None, repository_path=None)` - Stash changes
- `apply_stash(stash_ref=None, repository_path=None)` - Apply stash
- `list_stashes(repository_path=None)` - List stashes

### Advanced Operations (1)
- `cherry_pick(commit_sha, repository_path=None, no_commit=False)` - Cherry-pick commit

### GitHub API Operations (6)
- `create_github_repository(name, private=True, ...)` - Create GitHub repo
- `delete_github_repository(owner, repo_name, ...)` - Delete GitHub repo
- `create_pull_request(repo_owner, repo_name, ...)` - Create PR
- `get_pull_requests(repo_owner, repo_name, ...)` - Get PRs
- `get_pull_request(repo_owner, repo_name, pr_number, ...)` - Get specific PR
- `get_repository_info(repo_owner, repo_name, ...)` - Get repo info

### Visualization Operations (6, optional)
- `create_git_analysis_report(repository_path, ...)` - Generate analysis report
- `visualize_git_branches(repository_path, ...)` - Visualize branch structure
- `visualize_commit_activity(repository_path, ...)` - Visualize commit activity
- `create_git_workflow_diagram(workflow_type, ...)` - Create workflow diagram
- `analyze_repository_structure(repository_path, ...)` - Analyze repo structure
- `get_repository_metadata(repository_path)` - Get repository metadata

## Integration

### With Logging

The module automatically uses the `logging_monitoring` module for all operations:

```python
from codomyrmex.logging_monitoring import setup_logging
from codomyrmex.git_operations import commit_changes

# Setup logging (typically done once at application start)
setup_logging()

# All Git operations are automatically logged
commit_changes("Add feature", "/path/to/repo")
```

### With Performance Monitoring

Performance monitoring is automatically enabled when available:

```python
from codomyrmex.git_operations import clone_repository

# Performance is automatically tracked
clone_repository("https://github.com/user/repo.git", "/local/path")
```

### With Environment Setup

```python
from codomyrmex.environment_setup import check_dependencies
from codomyrmex.git_operations import check_git_availability

# Check dependencies
deps = check_dependencies(["git"])
if deps.get("git", {}).get("installed"):
    if check_git_availability():
        print("Git environment ready")
```

## Error Handling

All functions return typed results rather than raising exceptions:

- Boolean functions return `False` on error
- String functions return `None` on error
- Dictionary functions return empty dict or dict with `"error"` key
- List functions return empty list on error

Errors are logged via the `logging_monitoring` module. Check function return values and logs for error details.

```python
from codomyrmex.git_operations import commit_changes, get_status

# Check status before committing
status = get_status(repo_path)
if status.get("error"):
    print(f"Error: {status['error']}")
    return

# Attempt commit
success = commit_changes("Add feature", repo_path)
if not success:
    print("Commit failed - check logs for details")
```

## Security Considerations

See [SECURITY.md](SECURITY.md) for detailed security information. Key points:

- Credentials are managed by Git's credential system (SSH agent, credential manager)
- All Git commands use parameterized subprocess calls (no shell injection)
- Sensitive data is never logged
- Destructive operations require explicit confirmation

## Documentation

- **[API Specification](API_SPECIFICATION.md)** - Quick API reference
- **[Complete API Documentation](COMPLETE_API_DOCUMENTATION.md)** - Detailed function documentation
- **[Usage Examples](USAGE_EXAMPLES.md)** - Quick reference examples
- **[Comprehensive Usage Examples](COMPREHENSIVE_USAGE_EXAMPLES.md)** - Extensive examples
- **[Security Guide](SECURITY.md)** - Security best practices
- **[Technical Overview](docs/technical_overview.md)** - Technical architecture
- **[Tutorials](docs/tutorials/)** - Step-by-step guides

## Testing

Run tests with pytest:

```bash
# Run all tests
pytest src/codomyrmex/git_operations/tests/

# Run unit tests only
pytest src/codomyrmex/git_operations/tests/unit/

# Run integration tests only
pytest src/codomyrmex/git_operations/tests/integration/
```

## Requirements

- Python 3.10+
- Git installed and in PATH
- `requests` library (for GitHub API)
- Optional: `data_visualization` module (for visualization features)

## Directory Contents

### Core Files
- `__init__.py` - Module exports
- `git_manager.py` - Core Git operations
- `github_api.py` - GitHub API integration
- `repository_manager.py` - Repository management
- `repository_metadata.py` - Metadata system

### CLI Tools
- `repo_cli.py` - Repository CLI
- `metadata_cli.py` - Metadata CLI
- `github_library_generator.py` - Library generator

### Documentation
- `README.md` - This file
- `API_SPECIFICATION.md` - API reference
- `COMPLETE_API_DOCUMENTATION.md` - Full documentation
- `COMPREHENSIVE_USAGE_EXAMPLES.md` - Extensive examples
- `USAGE_EXAMPLES.md` - Quick examples
- `SECURITY.md` - Security guide
- `SPEC.md` - Functional specification
- `CHANGELOG.md` - Version history
- `AGENTS.md` - Agent coordination
- `docs/` - Additional documentation

### Data Files
- `repository_library.txt` - Repository library
- `repository_metadata.json` - Metadata storage

## Navigation

- **Technical Documentation**: [AGENTS.md](AGENTS.md)
- **Functional Specification**: [SPEC.md](SPEC.md)
- **API Reference**: [API_SPECIFICATION.md](API_SPECIFICATION.md)
- **Parent Directory**: [codomyrmex](../README.md)
- **Project Root**: [README](../../../README.md)
