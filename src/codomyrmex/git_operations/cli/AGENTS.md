# Codomyrmex Agents — src/codomyrmex/git_operations/cli

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Purpose

Provides command-line interfaces for Git operations including repository management, metadata tracking, and visualization demonstrations. These CLI tools enable interactive management of repository libraries, bulk operations, and Git visualization demos.

## Active Components

- `repo.py` - Repository Manager CLI for managing GitHub repositories
- `metadata.py` - Repository Metadata CLI for metadata management and reporting
- `demo.py` - Git Visualization Demo runner for sample data and live repository analysis
- `README.md` - Module documentation

## Key Classes and Functions

### repo.py
- **`cmd_list(manager, args)`** - Lists repositories with optional type/owner filtering
- **`cmd_search(manager, args)`** - Searches repositories by name, owner, or description
- **`cmd_clone(manager, args)`** - Clones single or bulk repositories with type/owner filters
- **`cmd_update(manager, args)`** - Updates (pulls) repositories, single or bulk
- **`cmd_status(manager, args)`** - Shows repository status including branch and changes
- **`cmd_summary(manager, args)`** - Prints repository library summary
- **`cmd_remote(manager, args)`** - Manages remotes (list, add, remove, prune)
- **`cmd_sync(manager, args)`** - Syncs repository (pull and push)
- **`cmd_prune(manager, args)`** - Prunes remote tracking branches
- **`cmd_clean(manager, args)`** - Cleans untracked files from repository

### metadata.py
- **`cmd_update_metadata(manager, args)`** - Updates metadata for single or bulk repositories
- **`cmd_show_metadata(manager, args)`** - Shows detailed metadata for a repository
- **`cmd_report(manager, args)`** - Generates comprehensive metadata reports with optional JSON export
- **`cmd_sync_status(manager, args)`** - Checks synchronization status of cloned repositories
- **`cmd_cleanup(manager, args)`** - Cleans up metadata for non-existent repositories

### demo.py
- **`GitVisualizationDemo`** - Class for running Git visualization demonstrations
- **`run_all_demos(repository_path, skip_sample, skip_workflows)`** - Runs all enabled demonstrations
- **`demo_sample_data_visualizations()`** - Demonstrates visualizations with sample data
- **`demo_real_repository_analysis(repository_path)`** - Analyzes a real Git repository
- **`demo_workflow_diagrams()`** - Generates workflow diagram demonstrations

## Operating Contracts

- All CLI commands use argparse for argument parsing with detailed help text
- Repository operations validate existence before attempting modifications
- Bulk operations use ThreadPoolExecutor for parallel execution (max_workers=4)
- Verbose mode provides detailed output for debugging and monitoring
- Error handling includes traceback output when verbose mode is enabled

## Signposting

- **Dependencies**: Requires `core/` submodule (RepositoryManager, RepositoryMetadataManager)
- **Parent Directory**: [git_operations](../README.md) - Parent module documentation
- **Related Modules**:
  - `core/repository.py` - RepositoryManager for Git operations
  - `core/metadata.py` - RepositoryMetadataManager for metadata tracking
  - `api/visualization.py` - Visualization functions for demo runner
- **Project Root**: [../../../../README.md](../../../../README.md) - Main project documentation
