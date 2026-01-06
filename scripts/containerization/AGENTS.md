# Codomyrmex Agents — scripts/containerization

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

Containerization automation scripts providing command-line interfaces for Docker container management, building, and security scanning. This script module enables automated container workflows for Codomyrmex projects.

The containerization scripts serve as the primary interface for developers and DevOps teams to manage containerized applications and infrastructure.

## Module Overview

### Key Capabilities
- **Container Building**: Build Docker images from Dockerfiles and configurations
- **Container Management**: Manage container lifecycle and operations
- **Security Scanning**: Scan containers for vulnerabilities and security issues
- **Image Management**: Handle container image tagging, pushing, and registry operations
- **Multi-Platform Support**: Support for different container runtimes and registries

### Key Features
- Command-line interface with argument parsing
- Integration with core containerization modules
- Structured output formatting (JSON, text, verbose)
- Error handling and validation
- Logging integration for container operations tracking

## Function Signatures

### Core CLI Functions

```python
def main() -> None
```

Main CLI entry point for the containerization orchestrator.

**Command-line Usage:**
```bash
python orchestrate.py [command] [options]
```

**Available Commands:**
- `build` - Build Docker containers from configurations
- `scan` - Scan containers for security vulnerabilities

**Global Options:**
- `--verbose, -v` - Enable verbose output
- `--registry, -r` - Container registry URL

```python
def handle_build(args) -> None
```

Handle container building commands from CLI arguments.

**Parameters:**
- `args` - Parsed command-line arguments containing:
  - `dockerfile_path` (str): Path to Dockerfile
  - `context_path` (str, optional): Build context path. Defaults to Dockerfile directory
  - `image_name` (str): Name for the built image
  - `image_tag` (str, optional): Tag for the built image. Defaults to "latest"
  - `build_args` (dict, optional): Build-time arguments
  - `push` (bool, optional): Push image after building. Defaults to False
  - `platform` (str, optional): Target platform for multi-platform builds

**Returns:** None (builds container image and outputs results)

```python
def handle_scan(args) -> None
```

Handle container security scanning commands from CLI arguments.

**Parameters:**
- `args` - Parsed command-line arguments containing:
  - `image_name` (str): Name of the container image to scan
  - `scan_type` (str, optional): Type of security scan ("vulnerability", "compliance", "both"). Defaults to "vulnerability"
  - `output_format` (str, optional): Output format ("json", "table", "sarif"). Defaults to "table"
  - `severity_threshold` (str, optional): Minimum severity to report ("low", "medium", "high", "critical"). Defaults to "medium"
  - `ignore_unfixed` (bool, optional): Ignore vulnerabilities without fixes. Defaults to False

**Returns:** None (scans container and outputs security report)

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
4. **Security**: Handle container and registry credentials securely
5. **Resource Management**: Clean up temporary resources and containers

### Module-Specific Guidelines

#### Container Building
- Validate Dockerfiles and build contexts before building
- Support multi-stage builds and build caching
- Handle build failures with detailed error reporting
- Support different container registries and authentication

#### Security Scanning
- Support multiple security scanning tools and formats
- Provide actionable vulnerability reports
- Handle different severity levels and filtering options
- Integrate with CI/CD pipelines for automated scanning

#### Image Management
- Handle image tagging and versioning properly
- Support image signing and verification
- Provide image metadata and history information
- Manage registry authentication and access control

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
2. **Build Coordination**: Share container images with deployment scripts
3. **Security Integration**: Coordinate security scanning with other security tools
4. **Registry Management**: Share registry credentials and access patterns

### Quality Gates

Before script changes are accepted:

1. **CLI Testing**: All command-line options work correctly
2. **Build Testing**: Container building works with various configurations
3. **Scan Testing**: Security scanning produces accurate results
4. **Integration Testing**: Scripts work with core containerization modules

## Version History

- **v0.1.0** (December 2025) - Initial containerization automation scripts with building and security scanning capabilities