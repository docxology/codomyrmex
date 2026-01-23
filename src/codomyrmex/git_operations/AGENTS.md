# Codomyrmex Agents — src/codomyrmex/git_operations

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Purpose

Core Layer module providing a standardized interface for performing Git actions programmatically. Includes repository management, GitHub API integration, and visualization capabilities for branch analysis.

## Active Components

### Core Git Operations

- `core/git.py` - Core Git command wrappers
  - Key Functions: `clone_repository()`, `commit_changes()`, `push_changes()`, `pull_changes()`
  - Key Functions: `create_branch()`, `switch_branch()`, `merge_branch()`, `rebase_branch()`
  - Key Functions: `get_status()`, `get_diff()`, `get_commit_history()`
  - Key Functions: `stash_changes()`, `apply_stash()`, `cherry_pick()`

### Repository Management

- `core/repository.py` - Repository abstraction
  - Key Classes: `RepositoryManager`, `Repository`, `RepositoryType`

### Metadata Management

- `core/metadata.py` - Repository metadata
  - Key Classes: `RepositoryMetadataManager`, `RepositoryMetadata`, `CloneStatus`

### GitHub API

- `api/github.py` - GitHub API integration
  - Key Functions: `create_github_repository()`, `create_pull_request()`, `get_pull_requests()`
  - Key Functions: `get_repository_info()`, `delete_github_repository()`
  - Key Classes: `GitHubAPIError`

### Visualization (Optional)

- `api/visualization.py` - Git visualization
  - Key Functions: `visualize_git_branches()`, `visualize_commit_activity()`
  - Key Functions: `create_git_analysis_report()`, `create_git_workflow_diagram()`

## Key Classes and Functions

| Class/Function | Module | Purpose |
| :--- | :--- | :--- |
| `clone_repository()` | core/git | Clone a repository |
| `commit_changes()` | core/git | Create a commit |
| `push_changes()` | core/git | Push to remote |
| `create_branch()` | core/git | Create new branch |
| `merge_branch()` | core/git | Merge branches |
| `RepositoryManager` | core/repository | Manage multiple repositories |
| `create_pull_request()` | api/github | Create GitHub PR |
| `visualize_git_branches()` | api/visualization | Branch visualization |

## Operating Contracts

1. **Logging**: Uses `logging_monitoring` for all Git operation logging
2. **Environment**: Relies on `environment_setup` for Git availability checks
3. **Authentication**: GitHub operations require `GITHUB_TOKEN` environment variable
4. **Error Handling**: Raises specific exceptions for Git failures
5. **Visualization**: Optional - requires `data_visualization` module

## Signposting

### Document Hierarchy

- **Self**: [AGENTS.md](AGENTS.md)
- **Parent**: [src/codomyrmex/AGENTS.md](../AGENTS.md)
- **Project Root**: [../../../AGENTS.md](../../../AGENTS.md)

### Sibling Modules

| Module | AGENTS.md | Purpose |
| :--- | :--- | :--- |
| ci_cd_automation | [../ci_cd_automation/AGENTS.md](../ci_cd_automation/AGENTS.md) | CI/CD pipelines |
| build_synthesis | [../build_synthesis/AGENTS.md](../build_synthesis/AGENTS.md) | Build automation |
| agents | [../agents/AGENTS.md](../agents/AGENTS.md) | AI agents (includes git_agent) |

### Child Directories

| Directory | Purpose |
| :--- | :--- |
| core/ | Core Git operations |
| api/ | GitHub API and visualization |
| cli/ | CLI tools |
| tools/ | Git utilities |

### Related Documentation

- [README.md](README.md) - User documentation
- [API_SPECIFICATION.md](API_SPECIFICATION.md) - API documentation
- [SPEC.md](SPEC.md) - Functional specification
