# Codomyrmex Agents — scripts/physical_management

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: December 2025

## Purpose

Physical management automation scripts providing command-line interfaces for hardware resource monitoring, system information gathering, and physical infrastructure management. This script module enables automated physical resource monitoring for the Codomyrmex platform.

The physical_management scripts serve as the primary interface for system administrators and DevOps teams to monitor and manage physical computing resources.

## Module Overview

### Key Capabilities
- **System Information**: Gather comprehensive system and hardware information
- **Resource Monitoring**: Monitor physical resource usage and performance
- **Hardware Inventory**: Track hardware components and configurations
- **Performance Metrics**: Collect physical system performance data
- **Resource Management**: Manage physical resource allocation and optimization

### Key Features
- Command-line interface with argument parsing
- Integration with core physical management modules
- Structured output formatting (JSON, text, verbose)
- Error handling and validation
- Logging integration for physical resource tracking

## Function Signatures

### Core CLI Functions

```python
def main() -> None
```

Main CLI entry point for the physical management orchestrator.

**Command-line Usage:**
```bash
python orchestrate.py [command] [options]
```

**Available Commands:**
- `info` - Display physical system information

**Global Options:**
- `--verbose, -v` - Enable verbose output
- `--format, -f` - Output format (json, text, table)

```python
def handle_info(args) -> bool
```

Handle system information display command from CLI arguments.

**Parameters:**
- `args` - Parsed command-line arguments containing:
  - `category` (str, optional): Information category to display ("all", "cpu", "memory", "disk", "network")
  - `detailed` (bool, optional): Show detailed information. Defaults to False
  - `format` (str, optional): Output format. Defaults to "text"
  - `verbose` (bool, optional): Enable verbose output. Defaults to False

**Returns:** `bool` - True if information display completed successfully, False otherwise

**Raises:**
- `PhysicalManagementError`: When physical system information gathering fails

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
3. **System Compatibility**: Work across different operating systems
4. **Resource Efficiency**: Minimize system impact during monitoring
5. **Security**: Handle system information access securely

### Module-Specific Guidelines

#### System Information
- Provide comprehensive hardware and software information
- Support different information categories and detail levels
- Handle system-specific information gathering
- Provide cross-platform compatibility

#### Resource Monitoring
- Monitor CPU, memory, disk, and network resources
- Provide real-time and historical resource data
- Support different monitoring intervals and thresholds
- Handle resource monitoring across different platforms

#### Performance Metrics
- Collect detailed performance metrics
- Support different metric collection intervals
- Provide performance trend analysis
- Handle high-frequency data collection efficiently

## Navigation Links

### Module Documentation
- **Script Overview**: [README.md](README.md) - Complete script documentation

### Related Scripts

### Platform Navigation
- **Scripts Directory**: [../README.md](../README.md) - Scripts directory overview

## Agent Coordination

### Integration Points

When integrating with other scripts:

1. **Shared Utilities**: Use `_orchestrator_utils.py` for common CLI patterns
2. **Performance Integration**: Share physical metrics with performance scripts
3. **Monitoring Integration**: Coordinate with logging_monitoring scripts
4. **Resource Integration**: Share resource data with other management scripts

### Quality Gates

Before script changes are accepted:

1. **CLI Testing**: All command-line options work correctly
2. **System Testing**: Scripts work across different operating systems
3. **Resource Testing**: Physical monitoring doesn't impact system performance
4. **Information Testing**: System information gathering is accurate
5. **Integration Testing**: Scripts work with core physical management modules

## Version History

- **v0.1.0** (December 2025) - Initial physical management automation scripts with system information and resource monitoring capabilities
