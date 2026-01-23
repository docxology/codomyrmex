# Codomyrmex Agents — src/codomyrmex/git_operations/api

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Purpose

Provides GitHub API integration and Git visualization capabilities. This module handles programmatic interactions with GitHub repositories including repository management, pull requests, issues, and generates comprehensive Git visualization reports.

## Active Components

- `github.py` - GitHub REST API client for repository and PR management
- `visualization.py` - Git visualization integration with data_visualization module
- `README.md` - Module documentation

## Key Classes and Functions

### github.py
- **`GitHubAPIError`** - Custom exception for GitHub API errors
- **`create_github_repository(name, private, description, ...)`** - Creates new GitHub repositories with configurable options
- **`delete_github_repository(owner, repo_name, github_token)`** - Deletes a GitHub repository
- **`create_pull_request(repo_owner, repo_name, head_branch, base_branch, title, body)`** - Creates pull requests
- **`get_pull_requests(repo_owner, repo_name, state)`** - Lists pull requests with state filtering
- **`get_pull_request(repo_owner, repo_name, pr_number)`** - Gets detailed PR information
- **`get_repository_info(repo_owner, repo_name)`** - Retrieves comprehensive repository metadata
- **`create_issue(owner, repo_name, title, body, labels, assignees)`** - Creates GitHub issues
- **`list_issues(owner, repo_name, state, labels)`** - Lists repository issues
- **`close_issue(owner, repo_name, issue_number)`** - Closes an issue
- **`add_comment(owner, repo_name, issue_number, body)`** - Adds comments to issues/PRs

### visualization.py
- **`create_git_analysis_report(repository_path, output_dir, ...)`** - Creates comprehensive Git analysis reports with PNG and Mermaid diagrams
- **`visualize_git_branches(repository_path, output_path, format_type)`** - Generates branch visualization in PNG or Mermaid format
- **`visualize_commit_activity(repository_path, output_path, days_back)`** - Creates commit activity visualizations
- **`create_git_workflow_diagram(workflow_type, output_path, title)`** - Generates workflow diagrams for feature_branch, gitflow, or github_flow
- **`analyze_repository_structure(repository_path, output_path, max_depth)`** - Analyzes and visualizes repository structure
- **`get_repository_metadata(repository_path)`** - Gets comprehensive repository metadata for visualization

## Operating Contracts

- GitHub token is required via parameter or GITHUB_TOKEN environment variable
- All API calls use authenticated requests with proper error handling
- Visualization functions gracefully handle missing data_visualization module
- Repository path validation occurs before any Git operations
- Network errors are caught and logged with meaningful messages

## Signposting

- **Dependencies**: Requires `requests` for GitHub API, optional `data_visualization` for visualizations
- **Parent Directory**: [git_operations](../README.md) - Parent module documentation
- **Related Modules**:
  - `core/` - Core Git operations (git.py, repository.py)
  - `cli/` - Command-line interface for Git operations
  - `data_visualization/` - Visualization engines (GitVisualizer, MermaidDiagramGenerator)
- **Project Root**: [../../../../README.md](../../../../README.md) - Main project documentation
