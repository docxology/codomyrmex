# IDE Integration Module

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Overview

The IDE module provides programmatic integration and automation capabilities for various Integrated Development Environments. This enables AI agents to achieve maximum agentic operation of IDEs, allowing sophisticated control and automation of development workflows.

## Supported IDEs

| IDE | Submodule | Description |
|-----|-----------|-------------|
| **Antigravity** | `antigravity/` | Google DeepMind's Antigravity IDE integration |
| **Cursor** | `cursor/` | AI-first code editor integration |
| **VS Code** | `vscode/` | Visual Studio Code integration |

## Key Features

- **Abstract Base Client**: `IDEClient` provides a consistent API across all IDE integrations
- **Command Execution**: Execute IDE commands with timeout and error handling
- **Batch Operations**: Run multiple commands in sequence with optional stop-on-error
- **Event System**: Register handlers for IDE events
- **File Operations**: Open files, get active file, list open files
- **Command History**: Track executed commands with timing and success metrics

## Quick Start

```python
from codomyrmex.ide import CursorClient, IDECommand, IDEStatus

# Initialize IDE client
client = CursorClient()

# Connect to IDE
if client.connect():
    print(f"Status: {client.status}")  # IDEStatus.CONNECTED
    
    # Get currently active file
    active_file = client.get_active_file()
    print(f"Active: {active_file}")
    
    # Execute a command with error handling
    result = client.execute_command_safe("editor.action.formatDocument")
    if result.success:
        print(f"Formatted in {result.execution_time:.2f}s")
    
    # Batch execute commands
    commands = [
        IDECommand("editor.action.formatDocument"),
        IDECommand("editor.action.organizeImports"),
    ]
    results = client.execute_batch(commands)
    
    # Disconnect
    client.disconnect()
```

## Core Classes

| Class | Description |
|-------|-------------|
| `IDEClient` | Abstract base class for all IDE integrations |
| `IDECommand` | Represents an IDE command with args and timeout |
| `IDECommandResult` | Result of command execution with timing |
| `FileInfo` | Information about a file (path, language, line count) |
| `IDEStatus` | Enum for connection status (CONNECTED, DISCONNECTED, etc.) |

## Exceptions

| Exception | Description |
|-----------|-------------|
| `IDEError` | Base exception for IDE-related errors |
| `ConnectionError` | IDE connection failures |
| `CommandExecutionError` | Command execution failures |
| `SessionError` | Session-related errors |
| `ArtifactError` | Artifact operation failures |

## Navigation

- **Technical Documentation**: [AGENTS.md](AGENTS.md)
- **Functional Specification**: [SPEC.md](SPEC.md)
- **Parent Directory**: [codomyrmex](../README.md)
- **Project Root**: [README](../../../README.md)
