# Codomyrmex Agents - src/codomyrmex/ide

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Purpose

The IDE Integration module provides programmatic integration and automation capabilities for various Integrated Development Environments. It enables AI agents to achieve maximum agentic operation of IDEs themselves, allowing sophisticated control and automation of development workflows.

## Active Components

- `__init__.py` - Core IDE module defining abstract base classes and shared types for all IDE integrations
- `API_SPECIFICATION.md` - API documentation for the IDE module
- `SPEC.md` - Technical specification for IDE integrations
- `README.md` - Module documentation
- `antigravity/` - Integration with Google DeepMind's Antigravity IDE
- `cursor/` - Integration with Cursor AI-first code editor
- `vscode/` - Integration with Visual Studio Code

## Key Classes

- **IDEClient** - Abstract base class for all IDE integrations; defines the consistent API for connecting, disconnecting, executing commands, and managing files
- **IDEStatus** - Enumeration of connection states (DISCONNECTED, CONNECTING, CONNECTED, ERROR)
- **IDECommand** - Data class representing an IDE command with name, args, and timeout
- **IDECommandResult** - Data class containing execution results including success status, output, error, and timing
- **FileInfo** - Data class containing file metadata (path, name, language, line count, modified status)

## Operating Contracts

- All IDE-specific clients must inherit from `IDEClient` and implement all abstract methods
- Connection state must be properly tracked via `IDEStatus`
- Command execution should use `execute_command_safe()` for error handling and timing
- Event handlers can be registered via `register_event_handler()` for IDE events
- Command history is maintained and accessible via `command_history` property

## Signposting

- **Parent Directory**: [codomyrmex](../README.md) - Main package documentation
- **Submodules**:
  - [antigravity/](./antigravity/README.md) - Antigravity IDE integration
  - [cursor/](./cursor/README.md) - Cursor IDE integration
  - [vscode/](./vscode/README.md) - VSCode integration
- **Project Root**: [../../../README.md](../../../README.md) - Main project documentation
