# Personal AI Infrastructure — Git Operations Module

**Version**: v0.2.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

The Git Operations module is a comprehensive **programmatic Git interface** for the codomyrmex ecosystem. It provides 30+ core git functions, GitHub API operations, repository management classes, and optional visualization integration. This is a **Core Layer** module that PAI agents use extensively during BUILD, EXECUTE, and VERIFY phases.

## PAI Capabilities

### Core Git Operations (25+ Functions)

```python
from codomyrmex.git_operations import (
    # Repository checks
    check_git_availability, is_git_repository, initialize_git_repository,
    clone_repository,
    # Branch operations
    create_branch, switch_branch, get_current_branch,
    merge_branch, rebase_branch,
    # File & commit operations
    add_files, commit_changes, amend_commit,
    get_status, get_diff, reset_changes,
    # Remote operations
    push_changes, pull_changes, fetch_changes,
    add_remote, remove_remote, list_remotes,
    # History
    get_commit_history,
    # Config
    get_config, set_config,
    # Advanced
    cherry_pick,
    # Tags
    create_tag, list_tags,
    # Stash
    stash_changes, apply_stash, list_stashes,
)

# Example: Get repository status
status = get_status("/path/to/repo")
branch = get_current_branch("/path/to/repo")
diff = get_diff("/path/to/repo")
```

### GitHub API Operations

```python
from codomyrmex.git_operations import (
    create_github_repository, delete_github_repository,
    create_pull_request, get_pull_requests, get_pull_request,
    get_repository_info, GitHubAPIError,
)

# Create a PR
pr = create_pull_request(
    owner="org", repo="project",
    title="Add feature", body="Description",
    head="feature-branch", base="main",
)
```

### Repository Management

```python
from codomyrmex.git_operations import (
    Repository, RepositoryManager, RepositoryType,
    RepositoryMetadataManager, RepositoryMetadata, CloneStatus,
)

manager = RepositoryManager()
repo = manager.get_repository("/path/to/repo")
metadata = RepositoryMetadataManager(repo)
```

### Visualization (Optional)

When visualization dependencies are available:

```python
from codomyrmex.git_operations import (
    create_git_analysis_report,
    visualize_git_branches,
    visualize_commit_activity,
    create_git_workflow_diagram,
    analyze_repository_structure,
    get_repository_metadata,
)
```

### CLI Commands

```bash
codomyrmex git_operations status  # Show git status for current directory
codomyrmex git_operations info    # Show repository info (branch, remotes, path)
```

## Key Exports

| Category | Exports | Count |
|----------|---------|-------|
| **Core Git** | `check_git_availability`, `is_git_repository`, `clone_repository`, `create_branch`, `switch_branch`, `get_current_branch`, `merge_branch`, `rebase_branch`, `add_files`, `commit_changes`, `amend_commit`, `get_status`, `get_diff`, `reset_changes`, `push_changes`, `pull_changes`, `fetch_changes`, `add_remote`, `remove_remote`, `list_remotes`, `get_commit_history`, `get_config`, `set_config`, `cherry_pick`, `create_tag`, `list_tags`, `stash_changes`, `apply_stash`, `list_stashes` | 29 |
| **Repository** | `Repository`, `RepositoryManager`, `RepositoryType`, `RepositoryMetadataManager`, `RepositoryMetadata`, `CloneStatus` | 6 |
| **GitHub API** | `create_github_repository`, `delete_github_repository`, `create_pull_request`, `get_pull_requests`, `get_pull_request`, `get_repository_info`, `GitHubAPIError` | 7 |
| **Visualization** | `create_git_analysis_report`, `visualize_git_branches`, `visualize_commit_activity`, `create_git_workflow_diagram`, `analyze_repository_structure`, `get_repository_metadata` | 6 (optional) |

## MCP Integration

The MCP server exposes `git_status` and `git_diff` tools that delegate to this module's `get_status()` and `get_diff()` functions. These are among the most-used tools during PAI OBSERVE phase.

## PAI Algorithm Phase Mapping

| Phase | Git Operations Contribution |
|-------|---------------------------|
| **OBSERVE** | `get_status`, `get_diff`, `get_current_branch`, `get_commit_history` — understand repository state |
| **PLAN** | `list_remotes`, `get_repository_info` — assess project structure and remote configuration |
| **BUILD** | `create_branch`, `add_files`, `commit_changes` — create artifacts and version them |
| **EXECUTE** | `push_changes`, `pull_changes`, `merge_branch`, `create_pull_request` — execute git workflows |
| **VERIFY** | `get_diff` — validate changes match intent; `get_status` — confirm clean state |
| **LEARN** | `get_commit_history` — review past changes for patterns |

## Architecture Role

**Core Layer** — Depends on `logging_monitoring` and `environment_setup` (Foundation). Used by Service and Application layer modules for version control operations.

## Navigation

- **Self**: [PAI.md](PAI.md)
- **Parent**: [../PAI.md](../PAI.md) — Source-level PAI module map
- **Root Bridge**: [../../../PAI.md](../../../PAI.md) — Authoritative PAI system bridge doc
- **Siblings**: [README.md](README.md) | [AGENTS.md](AGENTS.md) | [SPEC.md](SPEC.md) | [API_SPECIFICATION.md](API_SPECIFICATION.md)
- **MCP Bridge**: [../model_context_protocol/PAI.md](../model_context_protocol/PAI.md) — MCP tools that wrap git operations
