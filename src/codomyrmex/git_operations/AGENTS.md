# Codomyrmex Agents — src/codomyrmex/git_operations

## Signposting
- **Parent**: [codomyrmex](../AGENTS.md)
- **Self**: [Agents](AGENTS.md)
- **Children**:
    - [docs](docs/AGENTS.md)
    - [tests](tests/AGENTS.md)
- **Key Artifacts**:
    - [Functional Spec](SPEC.md)
    - [Human Readme](README.md)

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Purpose
Module components and implementation for git_operations. Provides comprehensive Git operations API with 40+ functions covering repository management, branching, commits, remotes, GitHub API integration, and optional visualization features.

## Active Components

### Core Implementation Files
- `__init__.py` – Module exports and public API
- `git_manager.py` – Core Git operations using subprocess
- `github_api.py` – GitHub API integration
- `repository_manager.py` – Repository library management
- `repository_metadata.py` – Metadata tracking system
- `visualization_integration.py` – Optional visualization features

### CLI Tools
- `repo_cli.py` – Repository management CLI
- `metadata_cli.py` – Metadata management CLI
- `github_library_generator.py` – Generate repository libraries from GitHub API

### Documentation Files
- `README.md` – Comprehensive module overview
- `API_SPECIFICATION.md` – API reference
- `COMPLETE_API_DOCUMENTATION.md` – Detailed function documentation
- `COMPREHENSIVE_USAGE_EXAMPLES.md` – Extensive usage examples
- `USAGE_EXAMPLES.md` – Quick reference examples
- `SECURITY.md` – Security considerations
- `SPEC.md` – Functional specification
- `CHANGELOG.md` – Version history
- `MCP_TOOL_SPECIFICATION.md` – MCP tool specification (currently N/A)
- `METADATA_SYSTEM_GUIDE.md` – Metadata system documentation
- `REPOSITORY_MANAGEMENT_GUIDE.md` – Repository management guide

### Configuration Files
- `.gitignore` – Git ignore patterns (includes backup file patterns)
- `.cursor/.cursorrules` – Module-specific cursor rules
- `requirements.txt` – Deprecated (dependencies in pyproject.toml)

### Data Files
- `repository_library.txt` – Repository library
- `auto_generated_library.txt` – Auto-generated repository library
- `docxology_repository_library.txt` – Docxology-specific library
- `repository_metadata.json` – Metadata storage

### Directories
- `docs/` – Documentation directory
- `tests/` – Test suites directory

## Key Functions

### Core Operations
- `check_git_availability()` – Verify Git installation
- `is_git_repository(path)` – Check if path is Git repository
- `initialize_git_repository(path, initial_commit=True)` – Create new repository
- `clone_repository(url, destination, branch=None)` – Clone remote repository

### Branch Operations
- `create_branch(branch_name, repository_path=None)` – Create and switch to branch
- `switch_branch(branch_name, repository_path=None)` – Switch to branch
- `get_current_branch(repository_path=None)` – Get current branch
- `merge_branch(source_branch, target_branch, repository_path=None)` – Merge branches
- `rebase_branch(target_branch, repository_path=None)` – Rebase branch

### File Operations
- `add_files(file_paths, repository_path=None)` – Stage files
- `commit_changes(message, repository_path=None, ...)` – Commit changes
- `amend_commit(message=None, repository_path=None, ...)` – Amend commit
- `get_status(repository_path=None)` – Get repository status
- `get_diff(file_path=None, staged=False, repository_path=None)` – Get diff
- `reset_changes(mode="mixed", target="HEAD", repository_path=None)` – Reset changes

### Remote Operations
- `push_changes(remote="origin", branch=None, repository_path=None)` – Push to remote
- `pull_changes(remote="origin", branch=None, repository_path=None)` – Pull from remote
- `fetch_changes(remote="origin", branch=None, repository_path=None)` – Fetch from remote
- `add_remote(remote_name, url, repository_path=None)` – Add remote
- `remove_remote(remote_name, repository_path=None)` – Remove remote
- `list_remotes(repository_path=None)` – List remotes

### History & Information
- `get_commit_history(limit=10, repository_path=None)` – Get commit history
- `get_commit_history_filtered(...)` – Get filtered commit history

### Config Operations
- `get_config(key, repository_path=None, global_config=False)` – Get Git config
- `set_config(key, value, repository_path=None, global_config=False)` – Set Git config

### Tag Operations
- `create_tag(tag_name, message=None, repository_path=None)` – Create tag
- `list_tags(repository_path=None)` – List tags

### Stash Operations
- `stash_changes(message=None, repository_path=None)` – Stash changes
- `apply_stash(stash_ref=None, repository_path=None)` – Apply stash
- `list_stashes(repository_path=None)` – List stashes

### Advanced Operations
- `cherry_pick(commit_sha, repository_path=None, no_commit=False)` – Cherry-pick commit

### GitHub API Operations
- `create_github_repository(name, private=True, ...)` – Create GitHub repo
- `delete_github_repository(owner, repo_name, ...)` – Delete GitHub repo
- `create_pull_request(repo_owner, repo_name, ...)` – Create PR
- `get_pull_requests(repo_owner, repo_name, ...)` – Get PRs
- `get_pull_request(repo_owner, repo_name, pr_number, ...)` – Get specific PR
- `get_repository_info(repo_owner, repo_name, ...)` – Get repo info

### Visualization Operations (Optional)
- `create_git_analysis_report(repository_path, ...)` – Generate analysis report
- `visualize_git_branches(repository_path, ...)` – Visualize branch structure
- `visualize_commit_activity(repository_path, ...)` – Visualize commit activity
- `create_git_workflow_diagram(workflow_type, ...)` – Create workflow diagram
- `analyze_repository_structure(repository_path, ...)` – Analyze repo structure
- `get_repository_metadata(repository_path)` – Get repository metadata

## Operating Contracts
- Maintain alignment between code, documentation, and configured workflows.
- Ensure Model Context Protocol interfaces remain available for sibling agents.
- Record outcomes in shared telemetry and update TODO queues when necessary.
- All functions use subprocess with list arguments (never shell=True) for security.
- All functions return typed results (bool, str, dict, list) rather than raising exceptions.
- All operations are logged via logging_monitoring module.

## Dependencies
- **System**: Git CLI must be installed and in PATH
- **Python**: Python 3.10+
- **Internal**: `logging_monitoring`, `performance` (optional), `data_visualization` (optional)
- **External**: `requests` (for GitHub API)

## Navigation Links
- **Human Documentation**: [README.md](README.md)
- **Functional Specification**: [SPEC.md](SPEC.md)
- **API Reference**: [API_SPECIFICATION.md](API_SPECIFICATION.md)
- **Complete Documentation**: [COMPLETE_API_DOCUMENTATION.md](COMPLETE_API_DOCUMENTATION.md)
- **📁 Parent Directory**: [codomyrmex](../README.md) - Parent directory documentation
- **🏠 Project Root**: [README](../../../README.md) - Main project documentation
