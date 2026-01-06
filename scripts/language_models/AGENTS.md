# Codomyrmex Agents — scripts/language_models

## Signposting
- **Parent**: [Scripts](../AGENTS.md)
- **Self**: [Agents](AGENTS.md)
- **Children**:
    - None
- **Key Artifacts**:
    - [Functional Spec](SPEC.md)
    - [Human Readme](README.md)

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: December 2025

## Purpose

Language model automation scripts providing command-line interfaces for language model management, configuration, and availability checking. This script module enables automated language model workflows for Codomyrmex projects.

The language_models scripts serve as the primary interface for AI/ML engineers and developers to manage language model operations and configurations.

## Module Overview

### Key Capabilities
- **Model Availability**: Check and validate language model availability
- **Model Listing**: List available models for different providers
- **Configuration Management**: Manage language model configurations
- **Multi-Provider Support**: Support for different language model providers
- **Performance Monitoring**: Monitor model performance and usage

### Key Features
- Command-line interface with argument parsing
- Integration with core language model modules
- Structured output formatting (JSON, text, verbose)
- Error handling and validation
- Logging integration for model operations tracking

## Function Signatures

### Core CLI Functions

```python
def main() -> None
```

Main CLI entry point for the language models orchestrator.

**Command-line Usage:**
```bash
python orchestrate.py [command] [options]
```

**Available Commands:**
- `check-availability` - Check language model availability
- `list-models` - List available models
- `config` - Manage language model configuration

**Global Options:**
- `--verbose, -v` - Enable verbose output
- `--provider, -p` - Language model provider

```python
def handle_check_availability(args) -> None
```

Handle model availability checking commands from CLI arguments.

**Parameters:**
- `args` - Parsed command-line arguments containing:
  - `provider` (str, optional): Language model provider to check
  - `model` (str, optional): Specific model to check
  - `timeout` (int, optional): Timeout for availability check. Defaults to 30

**Returns:** None (checks model availability and outputs results)

```python
def handle_list_models(args) -> None
```

Handle model listing commands from CLI arguments.

**Parameters:**
- `args` - Parsed command-line arguments containing:
  - `provider` (str, optional): Provider to list models for
  - `filter` (str, optional): Filter criteria for model listing
  - `detailed` (bool, optional): Show detailed model information. Defaults to False

**Returns:** None (lists available models and outputs results)

```python
def handle_config(args) -> None
```

Handle configuration management commands from CLI arguments.

**Parameters:**
- `args` - Parsed command-line arguments containing:
  - `action` (str): Configuration action ("get", "set", "list", "validate")
  - `key` (str, optional): Configuration key for get/set operations
  - `value` (str, optional): Configuration value for set operations
  - `config_file` (str, optional): Path to configuration file

**Returns:** None (manages configuration and outputs results)

## Active Components

### Core Implementation
- `__init__.py` – Module initialization and public API exports
- `orchestrate.py` – Main CLI orchestrator script

### Documentation
- `README.md` – Script usage and overview
- `AGENTS.md` – This coordination document

### Supporting Files
- Integration with `_orchestrator_utils.py` for shared utilities


### Additional Files
- `SPEC.md` – Spec Md

## Operating Contracts

### Universal Script Protocols

All scripts in this module must:

1. **CLI Standards**: Follow consistent command-line argument patterns
2. **Error Handling**: Provide clear error messages and exit codes
3. **Logging Integration**: Use centralized logging for all operations
4. **Security**: Handle API keys and sensitive data securely
5. **Performance**: Monitor and report model performance metrics

### Module-Specific Guidelines

#### Model Availability
- Validate model accessibility and functionality
- Support different authentication methods
- Provide detailed availability reports
- Handle network and API errors gracefully

#### Model Management
- Support multiple language model providers
- Provide comprehensive model information
- Handle model versioning and updates
- Support model performance benchmarking

#### Configuration Management
- Support multiple configuration sources
- Validate configuration values and formats
- Provide secure storage of sensitive configuration
- Support configuration inheritance and overrides

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
2. **Configuration Sharing**: Share model configurations with other AI scripts
3. **Performance Monitoring**: Share model metrics with monitoring scripts
4. **Security Coordination**: Coordinate secure credential handling

### Quality Gates

Before script changes are accepted:

1. **CLI Testing**: All command-line options work correctly
2. **Model Testing**: Scripts work with various language model providers
3. **Configuration Testing**: Configuration management works correctly
4. **Security Testing**: Sensitive data handling is secure
5. **Integration Testing**: Scripts work with core language model modules

## Version History

- **v0.1.0** (December 2025) - Initial language model automation scripts with availability checking and configuration management