# Codomyrmex Agents — src/codomyrmex/git_operations

## Signposting
- **Parent**: [codomyrmex](../AGENTS.md)
- **Self**: [Git Operations Agents](AGENTS.md)
- **Children**:
    - [docs](docs/AGENTS.md)
    - [tests](tests/AGENTS.md)
- **Key Artifacts**:
    - [Functional Spec](SPEC.md)
    - [Human Readme](README.md)

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: December 2025

## Purpose

Core module providing comprehensive Git version control automation capabilities for the Codomyrmex platform. This module enables programmatic interaction with Git repositories, supporting common version control workflows, repository analysis, and automated Git operations.

The git_operations module serves as the version control backbone, enabling automated development workflows and repository management throughout the platform.

## Module Overview

### Key Capabilities
- **Repository Management**: Initialize, clone, and manage Git repositories
- **Branch Operations**: Create, switch, merge, and delete branches
- **Commit Automation**: Stage files, create commits, and manage commit messages
- **Repository Analysis**: Analyze repository history, contributors, and changes
- **Remote Operations**: Push, pull, and synchronize with remote repositories
- **Status Monitoring**: Track repository state, changes, and conflicts

### Key Features
- Comprehensive Git command abstraction with Python API
- Repository state analysis and reporting
- Automated workflow support for CI/CD integration
- Error handling and conflict resolution support
- Integration with logging system for operation tracking

## Function Signatures

### Repository Management Functions

```python
def check_git_availability() -> bool
```

Check if Git is available on the system.

**Returns:** `bool` - True if Git is available and functional

```python
def is_git_repository(path: str = None) -> bool
```

Check if the given path is a Git repository.

**Parameters:**
- `path` (str, optional): Path to check. Defaults to current working directory

**Returns:** `bool` - True if path is a Git repository

```python
def initialize_git_repository(path: str, initial_commit: bool = True) -> bool
```

Initialize a new Git repository at the specified path.

**Parameters:**
- `path` (str): Path where to initialize the repository
- `initial_commit` (bool): Whether to create an initial commit. Defaults to True

**Returns:** `bool` - True if initialization successful

```python
def clone_repository(url: str, destination: str, branch: str = None) -> bool
```

Clone a Git repository to the specified destination.

**Parameters:**
- `url` (str): Repository URL to clone
- `destination` (str): Local path where to clone
- `branch` (str, optional): Branch to clone. Defaults to repository default

**Returns:** `bool` - True if cloning successful

### Branch Operations Functions

```python
def create_branch(branch_name: str, repository_path: str = None) -> bool
```

Create a new branch from the current HEAD.

**Parameters:**
- `branch_name` (str): Name of the new branch
- `repository_path` (str, optional): Repository path. Defaults to current directory

**Returns:** `bool` - True if branch creation successful

```python
def switch_branch(branch_name: str, repository_path: str = None) -> bool
```

Switch to the specified branch.

**Parameters:**
- `branch_name` (str): Name of branch to switch to
- `repository_path` (str, optional): Repository path. Defaults to current directory

**Returns:** `bool` - True if branch switch successful

```python
def get_current_branch(repository_path: str = None) -> Optional[str]
```

Get the name of the currently active branch.

**Parameters:**
- `repository_path` (str, optional): Repository path. Defaults to current directory

**Returns:** `Optional[str]` - Branch name or None if not in a repository

### File and Commit Operations Functions

```python
def add_files(file_paths: list[str], repository_path: str = None) -> bool
```

Stage files for commit.

**Parameters:**
- `file_paths` (list[str]): List of file paths to stage
- `repository_path` (str, optional): Repository path. Defaults to current directory

**Returns:** `bool` - True if staging successful

```python
def commit_changes(
    message: str,
    file_paths: list[str] = None,
    repository_path: str = None
) -> str
```

Create a commit with staged changes.

**Parameters:**
- `message` (str): Commit message
- `file_paths` (list[str], optional): Specific files to commit. If None, commits all staged changes
- `repository_path` (str, optional): Repository path. Defaults to current directory

**Returns:** `str` - Commit hash if successful, error message otherwise

### Remote Operations Functions

```python
def push_changes(
    remote: str = "origin",
    branch: str = None,
    repository_path: str = None
) -> bool
```

Push commits to a remote repository.

**Parameters:**
- `remote` (str): Remote name. Defaults to "origin"
- `branch` (str, optional): Branch to push. Defaults to current branch
- `repository_path` (str, optional): Repository path. Defaults to current directory

**Returns:** `bool` - True if push successful

```python
def pull_changes(
    remote: str = "origin",
    branch: str = None,
    repository_path: str = None
) -> bool
```

Pull changes from a remote repository.

**Parameters:**
- `remote` (str): Remote name. Defaults to "origin"
- `branch` (str, optional): Branch to pull. Defaults to current branch
- `repository_path` (str, optional): Repository path. Defaults to current directory

**Returns:** `bool` - True if pull successful

### Status and Information Functions

```python
def get_status(repository_path: str = None) -> dict[str, any]
```

Get repository status information.

**Parameters:**
- `repository_path` (str, optional): Repository path. Defaults to current directory

**Returns:** `dict[str, any]` - Dictionary containing status information

```python
def get_commit_history(
    limit: int = 10,
    repository_path: str = None,
    detailed: bool = False
) -> list[dict[str, any]]
```

Get commit history for the repository.

**Parameters:**
- `limit` (int): Maximum number of commits to return. Defaults to 10
- `repository_path` (str, optional): Repository path. Defaults to current directory
- `detailed` (bool): Whether to include detailed commit information. Defaults to False

**Returns:** `list[dict[str, any]]` - List of commit information dictionaries

### GitHub API Functions

```python
def create_github_repository(
    name: str,
    description: str = "",
    private: bool = False,
    token: str = None
) -> dict[str, any]
```

Create a new repository on GitHub.

**Parameters:**
- `name` (str): Repository name
- `description` (str): Repository description. Defaults to empty string
- `private` (bool): Whether repository should be private. Defaults to False
- `token` (str, optional): GitHub API token. Uses environment variable if not provided

**Returns:** `dict[str, any]` - Repository information from GitHub API

## Active Components

### Core Implementation
- `__init__.py` – Module initialization and public API exports
- `git_manager.py` – Main Git operations engine and repository management
- `repository_manager.py` – Advanced repository management utilities

### GitHub Integration
- `github_api.py` – GitHub API client for remote operations
- `github_library_generator.py` – Repository library generation tools

### CLI Tools
- `repo_cli.py` – Command-line interface for repository operations
- `metadata_cli.py` – Metadata management command-line tools

### Documentation
- `README.md` – Module usage and overview
- `API_SPECIFICATION.md` – Complete API documentation
- `COMPLETE_API_DOCUMENTATION.md` – Detailed API reference
- `USAGE_EXAMPLES.md` – Practical usage demonstrations
- `COMPREHENSIVE_USAGE_EXAMPLES.md` – Advanced usage examples
- `REPOSITORY_MANAGEMENT_GUIDE.md` – Repository management guide
- `METADATA_SYSTEM_GUIDE.md` – Metadata system documentation
- `MCP_TOOL_SPECIFICATION.md` – AI agent tool specifications
- `SECURITY.md` – Security considerations for Git operations
- `CHANGELOG.md` – Version history and updates

### Data and Libraries
- `repository_metadata.json` – Repository metadata storage
- `repository_library.txt` – Repository library data
- `auto_generated_library.txt` – Auto-generated library files
- Various backup files for metadata preservation

### Supporting Files
- `requirements.txt` – Module dependencies (GitPython, PyGitHub, etc.)
- `docs/` – Additional documentation
- `tests/` – Comprehensive test suite
- `visualization_integration.py` – Integration with visualization modules


### Additional Files
- `SPEC.md` – Spec Md
- `__pycache__` –   Pycache  
- `docs` – Docs
- `docxology_repository_library.txt` – Docxology Repository Library Txt
- `repository_metadata.json.backup.20260105_140649` – Repository Metadata Json Backup 20260105 140649
- `repository_metadata.py` – Repository Metadata Py
- `tests` – Tests

## Operating Contracts

### Universal Git Protocols

All Git operations within the Codomyrmex platform must:

1. **Repository Integrity** - Operations should preserve repository state and history
2. **Authentication Security** - Handle credentials securely without exposure
3. **Error Recovery** - Provide rollback mechanisms for failed operations
4. **Performance Aware** - Optimize operations for large repositories
5. **Audit Trail** - Log all Git operations for tracking and debugging

### Module-Specific Guidelines

#### Repository Operations
- Validate repository state before performing operations
- Handle merge conflicts with clear error reporting
- Support both local and remote repository operations
- Provide progress feedback for long-running operations

#### Branch Management
- Implement safe branch switching with working directory preservation
- Support branch creation, deletion, and renaming operations
- Handle branch merging with conflict detection and resolution
- Track branch relationships and hierarchies

#### Commit Automation
- Generate meaningful commit messages when not provided
- Support selective staging and partial commits
- Validate commit contents before execution
- Handle commit signing and verification

## Navigation Links
- **Human Documentation**: [README.md](README.md)
- **Functional Specification**: [SPEC.md](SPEC.md)

### Module Documentation
- **Module Overview**: [README.md](README.md) - Complete module documentation
- **API Reference**: [API_SPECIFICATION.md](API_SPECIFICATION.md) - Detailed API specification (if applicable)
- **Usage Examples**: [USAGE_EXAMPLES.md](USAGE_EXAMPLES.md) - Practical usage demonstrations (if applicable)

### Platform Navigation
- **Parent Directory**: [codomyrmex](../README.md) - Package overview
- **Project Root**: [README](../../../README.md) - Main project documentation
- **Source Root**: [src](../../README.md) - Source code documentation