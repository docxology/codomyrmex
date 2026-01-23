# Codomyrmex Agents - src/codomyrmex/ide/vscode

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Purpose

The VS Code integration module provides programmatic access to Visual Studio Code's Extension API, workspace management, debugging capabilities, and settings configuration. It enables automation of common VS Code workflows and extension interactions.

## Active Components

- `__init__.py` - VSCodeClient implementation for VS Code automation
- `SPEC.md` - Technical specification for VS Code integration
- `README.md` - Module documentation

## Key Classes

- **VSCodeClient** - Client for interacting with Visual Studio Code, extends `IDEClient`
  - `connect()` - Establish connection by detecting `.vscode` directory or `.code-workspace` files
  - `list_extensions()` - List installed extensions with metadata (name, publisher, version, enabled status)
  - `list_commands()` - List available VS Code commands
  - `get_settings()` - Get workspace settings from `.vscode/settings.json`
  - `update_settings(settings)` - Update workspace settings with merge behavior
  - `start_debug(config)` - Start a debug session with optional configuration
  - `stop_debug()` - Stop the current debug session

## Operating Contracts

- Workspace detection is based on presence of `.vscode` directory or `*.code-workspace` files
- Settings are managed via `.vscode/settings.json` with automatic creation of parent directories
- Extension listing provides common extension metadata (name, publisher, version)
- Debug operations require an active connection to VS Code
- All standard `IDEClient` methods are implemented

## Signposting

- **Parent Directory**: [ide/](../README.md) - IDE integrations module
- **Sibling Modules**:
  - [cursor/](../cursor/README.md) - Cursor IDE integration
  - [antigravity/](../antigravity/README.md) - Antigravity integration
- **Project Root**: [../../../../README.md](../../../../README.md) - Main project documentation
