# Codomyrmex Agents — scripts/config_management

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

Configuration management automation scripts providing command-line interfaces for loading, validating, and managing application configurations. This script module enables automated configuration handling for Codomyrmex projects.

The config_management scripts serve as the primary interface for developers and DevOps teams to manage configuration files and settings across different environments.

## Module Overview

### Key Capabilities
- **Configuration Loading**: Load configurations from various sources and formats
- **Configuration Validation**: Validate configuration files against schemas
- **Multi-Format Support**: Support for JSON, YAML, TOML, and environment variables
- **Environment Management**: Handle different configuration profiles
- **Security Handling**: Manage sensitive configuration data securely

### Key Features
- Command-line interface with argument parsing
- Integration with core configuration management modules
- Structured output formatting (JSON, text, verbose)
- Error handling and validation
- Logging integration for configuration tracking

## Function Signatures

### Core CLI Functions

```python
def main() -> None
```

Main CLI entry point for the configuration management orchestrator.

**Command-line Usage:**
```bash
python orchestrate.py [command] [options]
```

**Available Commands:**
- `load-config` - Load and merge configuration files
- `validate-config` - Validate configuration against schema

**Global Options:**
- `--verbose, -v` - Enable verbose output
- `--format, -f` - Output format (json, yaml, text)

```python
def handle_load_config(args) -> None
```

Handle configuration loading commands from CLI arguments.

**Parameters:**
- `args` - Parsed command-line arguments containing:
  - `config_files` (list): List of configuration files to load
  - `environment` (str, optional): Environment profile to use
  - `output_path` (str, optional): Output path for merged configuration
  - `override_values` (dict, optional): Key-value pairs to override configuration
  - `secrets_file` (str, optional): Path to secrets configuration file

**Returns:** None (loads and outputs merged configuration)

```python
def handle_validate_config(args) -> None
```

Handle configuration validation commands from CLI arguments.

**Parameters:**
- `args` - Parsed command-line arguments containing:
  - `config_file` (str): Path to configuration file to validate
  - `schema_file` (str, optional): Path to JSON schema file for validation
  - `strict` (bool, optional): Enable strict validation. Defaults to False
  - `check_secrets` (bool, optional): Validate secrets handling. Defaults to False

**Returns:** None (validates configuration and outputs validation results)

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
4. **Security**: Handle sensitive configuration data appropriately
5. **Validation**: Validate inputs and configuration integrity

### Module-Specific Guidelines

#### Configuration Loading
- Support multiple configuration formats and sources
- Handle configuration merging and precedence rules
- Provide clear error messages for configuration issues
- Support environment-specific configuration profiles

#### Configuration Validation
- Validate configuration structure and types
- Support JSON schema validation
- Check for required configuration values
- Validate cross-references between configuration sections

#### Security Handling
- Handle sensitive data appropriately
- Support encrypted configuration files
- Validate secrets access permissions
- Prevent accidental exposure of sensitive data

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
2. **Configuration Sharing**: Coordinate configuration loading across scripts
3. **Validation Coordination**: Share validation rules and schemas
4. **Security Integration**: Coordinate secure configuration handling

### Quality Gates

Before script changes are accepted:

1. **CLI Testing**: All command-line options work correctly
2. **Configuration Testing**: Scripts handle various configuration scenarios
3. **Validation Testing**: Configuration validation works accurately
4. **Integration Testing**: Scripts work with core configuration modules

## Version History

- **v0.1.0** (December 2025) - Initial configuration management automation scripts with loading and validation capabilities