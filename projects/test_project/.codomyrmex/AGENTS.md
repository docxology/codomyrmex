# Codomyrmex Agents — projects/test_project/.codomyrmex

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Signposting
- **Parent**: [test_project](../AGENTS.md)
- **Self**: [.codomyrmex Agents](AGENTS.md)
- **Children**:
    - None
- **Key Artifacts**:
    - [README](README.md)

## Purpose

Project-specific Codomyrmex configuration and state directory for the test project. This directory contains configuration files, cached data, and runtime state specific to the test project's Codomyrmex integration.

The .codomyrmex directory serves as the local configuration and state management area for Codomyrmex operations within this test project.

## Directory Overview

### Configuration Files
- Project-specific configuration overrides
- Module enablement settings
- Environment-specific parameters

### State Management
- Cached analysis results
- Session state and preferences
- Temporary working files

### Integration Points
- Links to global Codomyrmex configuration
- Project-specific module configurations
- Local overrides for global settings

## Active Components

### Configuration Management
- Local configuration files that override global defaults
- Project-specific module settings and preferences
- Environment-specific configuration overrides

### State Persistence
- Cached results from analysis and processing operations
- Session state for interactive workflows
- Temporary files and working directories

### Integration Files
- Links to parent Codomyrmex installation
- Local module discovery and registration
- Project-specific workflow definitions


### Additional Files
- `README.md` – Readme Md
- `project.json` – Project Json

## Operating Contracts

### Configuration Hierarchy

1. **Global Defaults** - Base configuration from main Codomyrmex installation
2. **Project Overrides** - Settings specific to this test project
3. **Environment Overrides** - Runtime environment-specific settings

### State Management

All state files should be:
- Properly versioned and recoverable
- Cleaned up on project reset
- Compatible with different Codomyrmex versions

### Integration Standards

Project integration must:
- Maintain compatibility with global Codomyrmex workflows
- Follow project-specific configuration patterns
- Support both interactive and automated usage modes

## Navigation Links

### Project Context
- **Parent Project**: [../README.md](../README.md) - Test project documentation

### Related Systems

## Agent Coordination

### Configuration Sync

When configuration changes occur:
1. Validate compatibility with global settings
2. Update local state and caches
3. Notify dependent modules of changes

### State Cleanup

Regular maintenance should include:
1. Clearing outdated caches
2. Removing temporary files
3. Validating configuration integrity

## Version History

- **v0.1.0** (February 2026) - Initial project-specific configuration directory structure
