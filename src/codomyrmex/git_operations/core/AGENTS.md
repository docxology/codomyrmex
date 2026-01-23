# Codomyrmex Agents — src/codomyrmex/git_operations/core

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Purpose

Provides core Git operations, repository management, and metadata tracking capabilities. This module implements the fundamental Git workflow operations (clone, commit, push, pull, branch, merge) and manages repository libraries with comprehensive metadata.

## Active Components

- `git.py` - Core Git operations manager with subprocess-based Git commands
- `repository.py` - Repository library manager with bulk operations support
- `metadata.py` - Repository metadata management with GitHub API integration
- `repository_metadata.json` - Persistent storage for repository metadata
- `README.md` - Module documentation

## Key Classes and Functions

### git.py
- **`check_git_availability()`** - Verifies Git is installed and accessible
- **`is_git_repository(path)`** - Checks if a path is a Git repository
- **`initialize_git_repository(path, initial_commit)`** - Initializes new Git repository
- **`clone_repository(url, destination, branch)`** - Clones a repository
- **`create_branch(branch_name, repository_path)`** - Creates and switches to new branch
- **`switch_branch(branch_name, repository_path)`** - Switches to existing branch
- **`get_current_branch(repository_path)`** - Gets current branch name
- **`add_files(file_paths, repository_path)`** - Stages files for commit
- **`commit_changes(message, repository_path, author_name, author_email)`** - Commits staged changes
- **`push_changes(remote, branch, repository_path)`** - Pushes to remote
- **`pull_changes(remote, branch, repository_path)`** - Pulls from remote
- **`get_status(repository_path)`** - Gets repository status (modified, added, deleted, untracked)
- **`get_commit_history(limit, repository_path)`** - Gets recent commits
- **`merge_branch(source_branch, target_branch, strategy)`** - Merges branches
- **`rebase_branch(target_branch, repository_path)`** - Rebases current branch
- **`create_tag(tag_name, message)`** / **`list_tags()`** - Tag management
- **`stash_changes(message)`** / **`apply_stash(stash_ref)`** / **`list_stashes()`** - Stash management
- **`add_remote(name, url)`** / **`remove_remote(name)`** / **`list_remotes()`** - Remote management
- **`reset_changes(mode, target)`** / **`revert_commit(commit_sha)`** - State management
- **`get_diff(target, cached)`** / **`get_blame(file_path)`** - Analysis tools
- **`cherry_pick(commit_sha)`** - Cherry-pick commits
- **`init_submodules()`** / **`update_submodules()`** - Submodule management

### repository.py
- **`RepositoryType`** - Enum: OWN, USE, FORK
- **`Repository`** - Dataclass representing a repository entry
- **`RepositoryManager`** - Manages repository library and Git operations
  - `list_repositories(repo_type)` - Lists repositories with optional type filter
  - `get_repository(full_name)` - Gets repository by full name
  - `search_repositories(query)` - Searches by name, owner, or description
  - `clone_repository(full_name, custom_path)` - Clones with metadata tracking
  - `update_repository(full_name)` - Pulls latest changes
  - `bulk_clone(repo_type, owner_filter, max_workers)` - Parallel bulk cloning
  - `bulk_update(repo_type, owner_filter, max_workers)` - Parallel bulk updating

### metadata.py
- **`RepositoryMetadataManager`** - Manages comprehensive repository metadata
- **`CloneStatus`** - Enum tracking clone state (NOT_CLONED, CLONED, ERROR, etc.)

## Operating Contracts

- All Git commands executed via subprocess with proper error handling
- Performance monitoring decorators applied to key operations
- Repository operations validate paths before execution
- Metadata automatically updated after successful clone/update operations
- Bulk operations use ThreadPoolExecutor for parallelization

## Signposting

- **Dependencies**: Uses `logging_monitoring` for logging, `performance` for monitoring
- **Parent Directory**: [git_operations](../README.md) - Parent module documentation
- **Related Modules**:
  - `api/github.py` - GitHub API integration
  - `cli/` - Command-line interfaces
  - `tools/` - Library generation utilities
- **Project Root**: [../../../../README.md](../../../../README.md) - Main project documentation
