# git_operations

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

Comprehensive programmatic Python interface for Git version control operations. Wraps Git subprocess calls into typed, error-handling functions covering repository lifecycle, branching, merging, stashing, tagging, remote management, and GitHub API integration. Includes optional visualization support for generating branch diagrams and commit activity charts.

## Key Exports

### Core Operations

- **`check_git_availability()`** -- Verify that git is installed and accessible
- **`is_git_repository()`** -- Check if a directory is a valid git repository
- **`initialize_git_repository()`** -- Initialize a new git repository in a directory
- **`clone_repository()`** -- Clone a remote repository to a local path

### Branch Operations

- **`create_branch()`** -- Create a new branch from the current HEAD or a specified commit
- **`switch_branch()`** -- Switch the working directory to a different branch
- **`get_current_branch()`** -- Return the name of the currently checked-out branch
- **`merge_branch()`** -- Merge a source branch into the current branch
- **`rebase_branch()`** -- Rebase the current branch onto a target branch

### File and Commit Operations

- **`add_files()`** -- Stage files for the next commit
- **`commit_changes()`** -- Create a new commit with staged changes
- **`amend_commit()`** -- Amend the most recent commit
- **`get_status()`** -- Return the working tree status
- **`get_diff()`** -- Show differences between commits, working tree, and index
- **`reset_changes()`** -- Reset staged or committed changes

### Remote Operations

- **`push_changes()`** -- Push local commits to a remote repository
- **`pull_changes()`** -- Pull and merge changes from a remote branch
- **`fetch_changes()`** -- Fetch updates from a remote without merging
- **`add_remote()`** -- Add a new remote repository
- **`remove_remote()`** -- Remove an existing remote
- **`list_remotes()`** -- List all configured remotes

### History, Config, and Advanced

- **`get_commit_history()`** -- Retrieve commit log entries
- **`get_config()` / `set_config()`** -- Read and write git configuration values
- **`cherry_pick()`** -- Apply a specific commit to the current branch
- **`create_tag()` / `list_tags()`** -- Create and list git tags
- **`stash_changes()` / `apply_stash()` / `list_stashes()`** -- Stash and restore uncommitted work

### Repository Management

- **`RepositoryManager`** -- High-level manager for multiple repository instances
- **`Repository`** -- Represents a single git repository with metadata
- **`RepositoryType`** -- Enum for repository classification (local, remote, fork, etc.)
- **`RepositoryMetadataManager`** -- Persists repository metadata to JSON
- **`RepositoryMetadata`** -- Dataclass holding repository metadata fields
- **`CloneStatus`** -- Enum tracking clone operation status

### GitHub API

- **`create_github_repository()`** -- Create a new repository on GitHub
- **`delete_github_repository()`** -- Delete a GitHub repository
- **`create_pull_request()`** -- Open a pull request
- **`get_pull_requests()` / `get_pull_request()`** -- List or retrieve pull request details
- **`get_repository_info()`** -- Fetch repository metadata from GitHub
- **`GitHubAPIError`** -- Exception for GitHub API failures

### Visualization (optional)

- **`create_git_analysis_report()`** -- Generate a full repository analysis report
- **`visualize_git_branches()`** -- Render branch topology diagrams
- **`visualize_commit_activity()`** -- Chart commit frequency over time
- **`create_git_workflow_diagram()`** -- Generate workflow diagrams
- **`analyze_repository_structure()`** -- Analyze file and directory structure
- **`get_repository_metadata()`** -- Extract metadata for visualization

## Directory Contents

- `core/` -- Core git operations (`git.py`), repository management (`repository.py`), and metadata persistence (`metadata.py`)
- `api/` -- GitHub REST API client (`github.py`) and visualization integration (`visualization.py`)
- `cli/` -- Command-line interface for git operations
- `data/` -- Data files and repository metadata JSON
- `docs/` -- Module-specific documentation
- `tools/` -- Additional git tooling utilities

## Navigation

- **Full Documentation**: [docs/modules/git_operations/](../../../docs/modules/git_operations/)
- **Parent Directory**: [codomyrmex](../README.md)
- **Project Root**: ../../../README.md
