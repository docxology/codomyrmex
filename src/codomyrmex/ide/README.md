# ide

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

Programmatic integration and automation framework for Integrated Development Environments. Provides an abstract `IDEClient` base class with a consistent API for connecting, executing commands, managing files, and handling events across multiple IDE backends. Enables AI agents to achieve full agentic operation of IDEs including Antigravity (Google DeepMind), Cursor, and VS Code.

## Key Exports

### Core Classes

- **`IDEClient`** -- Abstract base class for IDE integrations; defines the contract for connect/disconnect, command execution, file operations, batch execution, event handling, and command history tracking with success rate metrics
- **`CursorClient`** -- Concrete IDEClient implementation for the Cursor AI-first code editor

### Data Classes and Enums

- **`IDEStatus`** -- IDE session status: DISCONNECTED, CONNECTING, CONNECTED, ERROR
- **`IDECommand`** -- Represents an IDE command with name, args dict, and timeout
- **`IDECommandResult`** -- Result of command execution with success flag, output, error, and execution time
- **`FileInfo`** -- File metadata including path, name, modification status, detected language, and line count

### Exceptions

- **`IDEError`** -- Base exception for IDE operations
- **`ConnectionError`** -- Failed to connect to or communicate with the IDE (aliased from IDEConnectionError)
- **`CommandExecutionError`** -- Command execution failed within the IDE
- **`SessionError`** -- IDE session lifecycle error
- **`ArtifactError`** -- Error working with IDE artifacts

## Directory Contents

- `__init__.py` - Module definition with IDEClient ABC, data classes, and submodule imports
- `antigravity/` - Google DeepMind Antigravity IDE integration
- `cursor/` - Cursor AI-first code editor integration (CursorClient)
- `vscode/` - Visual Studio Code integration
- `AGENTS.md` - Agent integration specification
- `API_SPECIFICATION.md` - Detailed API documentation
- `SPEC.md` - Module specification
- `PAI.md` - PAI integration notes

## Navigation

- **Full Documentation**: [docs/modules/ide/](../../../docs/modules/ide/)
- **Parent Directory**: [codomyrmex](../README.md)
- **Project Root**: ../../../README.md
