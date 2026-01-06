# Codomyrmex Agents — scripts/environment_setup

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

Environment setup automation scripts providing command-line interfaces for environment validation, dependency checking, and configuration management. This script module enables automated environment preparation for Codomyrmex projects.

The environment_setup scripts serve as the primary interface for developers and DevOps teams to set up and validate development and deployment environments.

## Module Overview

### Key Capabilities
- **Dependency Checking**: Validate and install required dependencies
- **Environment Validation**: Check environment compatibility and requirements
- **UV Package Manager**: Manage Python environments with UV
- **Configuration Setup**: Set up environment variables and configurations
- **Multi-Platform Support**: Support for different operating systems and environments

### Key Features
- Command-line interface with argument parsing
- Integration with core environment setup modules
- Structured output formatting (JSON, text, verbose)
- Error handling and validation
- Logging integration for environment setup tracking

## Function Signatures

### Core CLI Functions

```python
def main() -> None
```

Main CLI entry point for the environment setup orchestrator.

**Command-line Usage:**
```bash
python orchestrate.py [command] [options]
```

**Available Commands:**
- `check-dependencies` - Check and validate project dependencies
- `setup-env-vars` - Set up environment variables
- `check-uv` - Validate UV package manager setup

**Global Options:**
- `--verbose, -v` - Enable verbose output
- `--fix` - Automatically fix issues when possible

```python
def handle_check_dependencies(args) -> None
```

Handle dependency checking commands from CLI arguments.

**Parameters:**
- `args` - Parsed command-line arguments containing:
  - `requirements_file` (str, optional): Path to requirements file. Defaults to "requirements.txt"
  - `python_version` (str, optional): Required Python version
  - `fix` (bool, optional): Automatically install missing dependencies. Defaults to False
  - `update` (bool, optional): Update dependencies to latest versions. Defaults to False

**Returns:** None (checks dependencies and outputs validation results)

```python
def handle_setup_env_vars(args) -> None
```

Handle environment variable setup commands from CLI arguments.

**Parameters:**
- `args` - Parsed command-line arguments containing:
  - `env_file` (str, optional): Path to .env file. Defaults to ".env"
  - `template_file` (str, optional): Path to environment template file
  - `overwrite` (bool, optional): Overwrite existing environment variables. Defaults to False
  - `interactive` (bool, optional): Prompt for missing values interactively. Defaults to False

**Returns:** None (sets up environment variables and outputs results)

```python
def handle_check_uv(args) -> None
```

Handle UV package manager validation commands from CLI arguments.

**Parameters:**
- `args` - Parsed command-line arguments containing:
  - `version` (str, optional): Required UV version
  - `install` (bool, optional): Install UV if not found. Defaults to False
  - `update` (bool, optional): Update UV to latest version. Defaults to False

**Returns:** None (validates UV installation and outputs results)

## Active Components

### Core Implementation
- `__init__.py` – Module initialization and public API exports
- `orchestrate.py` – Main CLI orchestrator script

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
4. **Non-Intrusive**: Avoid making permanent changes without explicit permission
5. **Cross-Platform**: Work across different operating systems and environments

### Module-Specific Guidelines

#### Dependency Management
- Support multiple package managers (pip, uv, conda)
- Validate dependency versions and compatibility
- Provide clear installation instructions for missing dependencies
- Handle virtual environment creation and activation

#### Environment Setup
- Support multiple environment variable sources (.env files, system variables)
- Validate environment variable values and formats
- Provide secure handling of sensitive environment variables
- Support environment-specific configurations

#### UV Integration
- Validate UV installation and version compatibility
- Provide UV installation and update capabilities
- Support UV-specific features and optimizations
- Integrate with UV's dependency locking and caching

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
2. **Dependency Sharing**: Share dependency information with other setup scripts
3. **Environment Coordination**: Coordinate environment variables across scripts
4. **UV Integration**: Share UV configuration and cache management

### Quality Gates

Before script changes are accepted:

1. **CLI Testing**: All command-line options work correctly
2. **Environment Testing**: Scripts work across different platforms and configurations
3. **Dependency Testing**: Dependency checking works with various package managers
4. **UV Testing**: UV integration works correctly and efficiently
5. **Integration Testing**: Scripts work with core environment setup modules

## Version History

- **v0.1.0** (December 2025) - Initial environment setup automation scripts with dependency checking and UV integration