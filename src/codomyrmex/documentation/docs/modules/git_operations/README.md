<!-- readme: generated -->

# git_operations

**Version**: v1.3.0 | **Status**: Active | **Source**: `src/codomyrmex/git_operations/`

## Overview

Git Operations Module for Codomyrmex.

The Git Operations module provides a standardized interface and tools for performing
Git actions programmatically within the Codomyrmex ecosystem.

Integration:
- Uses `logging_monitoring` for all logging (ensure `setup_logging()` is called in your main app).
- Relies on `environment_setup` for environment and dependency checks.

## Public Exports

`git_operations` exports 51 public symbols via `__all__`:

`CloneStatus`, `GitHubAPIError`, `Repository`, `RepositoryManager`, `RepositoryMetadata`, `RepositoryMetadataManager`, `RepositoryType`, `add_files`, `add_remote`, `amend_commit`, `apply_stash`, `check_git_availability`, `cherry_pick`, `clean_repository`, `cli_commands`, `clone_repository`, `commit_changes`, `create_branch`, `create_github_repository`, `create_pull_request`, `create_tag`, `delete_branch`, `delete_github_repository`, `fetch_changes` …

## Module Documentation

- Extended README: [readme.md](readme.md)
- Agent coordination: [AGENTS.md](AGENTS.md)
- Technical specification: [SPEC.md](SPEC.md)

## Navigation

- **All modules**: [../README.md](../README.md)
- **Source package**: [../../../../git_operations/](../../../../git_operations/)
