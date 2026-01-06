# Codomyrmex Agents — scripts/git_operations

## Signposting
- **Parent**: [Parent](../AGENTS.md)
- **Self**: [Agents](AGENTS.md)
- **Children**:
    - None
- **Key Artifacts**:
    - [Functional Spec](SPEC.md)
    - [Human Readme](README.md)

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: December 2025

## Purpose

Git operations automation scripts providing command-line interfaces for version control operations, repository management, and Git data visualization. This script module enables automated Git workflows for Codomyrmex projects.

The git_operations scripts serve as the primary interface for developers and teams to perform Git operations and analyze repository data.

## Module Overview

### Key Capabilities
- **Repository Operations**: Clone, status, branch management
- **File Operations**: Add, commit, push, pull operations
- **Repository Analysis**: Visualize Git repository data and workflows
- **Multi-Repository Support**: Handle multiple Git repositories
- **Visualization**: Generate charts and diagrams from Git data

### Key Features
- Command-line interface with argument parsing
- Integration with core Git operations modules
- Structured output formatting (JSON, text, verbose)
- Error handling and validation
- Logging integration for Git operations tracking

## Function Signatures

### Core CLI Functions (orchestrate.py)

```python
def main() -> None
```

Main CLI entry point for the Git operations orchestrator.

**Command-line Usage:**
```bash
python orchestrate.py [command] [options]
```

**Available Commands:**
- `status` - Show repository status
- `branch` - Manage branches
- `commit` - Create commits
- `add` - Stage files
- `push` - Push changes
- `pull` - Pull changes
- `clone` - Clone repositories

**Global Options:**
- `--repo-path, -r` - Repository path
- `--verbose, -v` - Enable verbose output

```python
def handle_status(args) -> None
```

Handle repository status commands from CLI arguments.

**Parameters:**
- `args` - Parsed command-line arguments containing:
  - `repo_path` (str, optional): Path to Git repository

**Returns:** None (displays repository status)

```python
def handle_branch(args) -> None
```

Handle branch management commands from CLI arguments.

**Parameters:**
- `args` - Parsed command-line arguments containing:
  - `repo_path` (str, optional): Path to Git repository
  - `action` (str): Branch action ("create", "switch", "delete", "list")
  - `branch_name` (str, optional): Branch name for create/switch operations

**Returns:** None (performs branch operation and outputs results)

```python
def handle_commit(args) -> None
```

Handle commit operations from CLI arguments.

**Parameters:**
- `args` - Parsed command-line arguments containing:
  - `repo_path` (str, optional): Path to Git repository
  - `message` (str): Commit message
  - `files` (list, optional): Specific files to commit

**Returns:** None (creates commit and outputs results)

```python
def handle_add(args) -> None
```

Handle file staging commands from CLI arguments.

**Parameters:**
- `args` - Parsed command-line arguments containing:
  - `repo_path` (str, optional): Path to Git repository
  - `files` (list): Files to stage

**Returns:** None (stages files and outputs results)

```python
def handle_push(args) -> None
```

Handle push operations from CLI arguments.

**Parameters:**
- `args` - Parsed command-line arguments containing:
  - `repo_path` (str, optional): Path to Git repository
  - `remote` (str, optional): Remote name. Defaults to "origin"
  - `branch` (str, optional): Branch to push

**Returns:** None (pushes changes and outputs results)

```python
def handle_pull(args) -> None
```

Handle pull operations from CLI arguments.

**Parameters:**
- `args` - Parsed command-line arguments containing:
  - `repo_path` (str, optional): Path to Git repository
  - `remote` (str, optional): Remote name. Defaults to "origin"
  - `branch` (str, optional): Branch to pull

**Returns:** None (pulls changes and outputs results)

```python
def handle_clone(args) -> None
```

Handle repository cloning commands from CLI arguments.

**Parameters:**
- `args` - Parsed command-line arguments containing:
  - `url` (str): Repository URL to clone
  - `destination` (str, optional): Local destination path
  - `branch` (str, optional): Branch to clone

**Returns:** None (clones repository and outputs results)

### Visualization Demo Functions (visualization_demo.py)

```python
def create_output_directory(base_name="git_visualization_demo")
```

Create output directory for visualization demo.

**Parameters:**
- `base_name` (str): Base name for output directory. Defaults to "git_visualization_demo"

**Returns:** Path to created output directory

```python
def demo_sample_data_visualizations(output_dir)
```

Generate visualizations from sample Git data.

**Parameters:**
- `output_dir` (str): Output directory for generated visualizations

**Returns:** None (creates sample data visualizations)

```python
def demo_real_repository_analysis(repository_path, output_dir)
```

Analyze and visualize a real Git repository.

**Parameters:**
- `repository_path` (str): Path to Git repository to analyze
- `output_dir` (str): Output directory for generated visualizations

**Returns:** None (analyzes repository and creates visualizations)

```python
def demo_workflow_diagrams(output_dir)
```

Generate Git workflow diagrams.

**Parameters:**
- `output_dir` (str): Output directory for generated diagrams

**Returns:** None (creates workflow diagrams)

```python
def main()
```

Main entry point for visualization demo.

**Returns:** None (runs complete visualization demo)

## Active Components

### Core Implementation
- `__init__.py` – Module initialization and public API exports
- `orchestrate.py` – Main CLI orchestrator script for Git operations
- `visualization_demo.py` – Git repository visualization demonstrations

### Documentation
- `README.md` – Script usage and overview
- `AGENTS.md` – This coordination document

### Supporting Files
- Integration with `_orchestrator_utils.py` for shared utilities

## Operating Contracts

### Universal Script Protocols

All scripts in this module must:

1. **CLI Standards**: Follow consistent command-line argument patterns
2. **Error Handling**: Provide clear error messages and exit codes
3. **Logging Integration**: Use centralized logging for all operations
4. **Git Safety**: Avoid destructive operations without confirmation
5. **Repository Validation**: Validate Git repository state before operations

### Module-Specific Guidelines

#### Git Operations
- Validate Git repository existence and accessibility
- Provide clear feedback for all Git operations
- Handle merge conflicts and other Git errors gracefully
- Support both local and remote Git operations

#### Visualization
- Generate meaningful visualizations from Git data
- Support multiple output formats for different use cases
- Handle large repositories efficiently
- Provide clear legends and documentation for visualizations

#### Repository Management
- Support operations on multiple repositories
- Provide repository status and health information
- Handle different Git configurations and remotes
- Support both interactive and automated operations

## Navigation Links
- **Human Documentation**: [README.md](README.md)
- **Functional Specification**: [SPEC.md](SPEC.md)

### Module Documentation
- **Script Overview**: [README.md](README.md) - Complete script documentation

### Related Scripts

### Platform Navigation
- **Scripts Directory**: [../README.md](../README.md) - Scripts directory overview

## Agent Coordination

### Integration Points

When integrating with other scripts:

1. **Shared Utilities**: Use `_orchestrator_utils.py` for common CLI patterns
2. **Repository Sharing**: Share repository information with other Git-related scripts
3. **Visualization Integration**: Share generated visualizations with documentation
4. **Workflow Coordination**: Coordinate Git operations with CI/CD pipelines

### Quality Gates

Before script changes are accepted:

1. **CLI Testing**: All command-line options work correctly
2. **Git Testing**: Scripts work with various Git repository configurations
3. **Visualization Testing**: Generated visualizations are accurate and useful
4. **Safety Testing**: Scripts avoid destructive operations
5. **Integration Testing**: Scripts work with core Git operations modules

## Version History

- **v0.1.0** (December 2025) - Initial Git operations automation scripts with repository management and visualization capabilities