# IDE Integration Module Documentation

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

IDE Integration Module.

## Key Features

- **IDEStatus** — Status of an IDE session.
- **IDECommand** — Represents an IDE command to be executed.
- **IDECommandResult** — Result of an IDE command execution.
- **FileInfo** — Information about a file in the IDE.
- **IDEClient** — Abstract base class for IDE integrations.
- `to_dict()` — to dict
- `to_dict()` — to dict
- `to_dict()` — to dict
- `status()` — Get the current connection status.

## Submodules

| Submodule | Description |
|-----------|-------------|
| `antigravity` | Antigravity IDE Integration |
| `cursor` | Cursor IDE Integration. |
| `vscode` | VS Code IDE Integration |

## Quick Start

```python
from codomyrmex.ide import IDEStatus, IDECommand, IDECommandResult

# Initialize
instance = IDEStatus()
```


## Installation

```bash
uv pip install codomyrmex
```

## API Reference

### Classes

| Class | Description |
|-------|-------------|
| `IDEStatus` | Status of an IDE session. |
| `IDECommand` | Represents an IDE command to be executed. |
| `IDECommandResult` | Result of an IDE command execution. |
| `FileInfo` | Information about a file in the IDE. |
| `IDEClient` | Abstract base class for IDE integrations. |

### Functions

| Function | Description |
|----------|-------------|
| `to_dict()` | to dict |
| `status()` | Get the current connection status. |
| `command_history()` | Get the history of executed commands. |
| `connect()` | Establish connection to the IDE. |
| `disconnect()` | Disconnect from the IDE. |
| `is_connected()` | Check if currently connected to the IDE. |
| `get_capabilities()` | Get the capabilities of this IDE integration. |
| `execute_command()` | Execute an IDE command. |
| `get_active_file()` | Get the path of the currently active file. |
| `open_file()` | Open a file in the IDE. |
| `get_open_files()` | Get list of currently open files. |
| `execute_command_safe()` | Execute a command with error handling and timing. |
| `execute_batch()` | Execute multiple commands in sequence. |
| `get_file_info()` | Get information about a file. |
| `register_event_handler()` | Register a handler for an IDE event. |
| `emit_event()` | Emit an event to all registered handlers. |
| `clear_command_history()` | Clear the command execution history. |
| `get_last_command()` | Get the most recent command result. |
| `get_success_rate()` | Calculate the command success rate. |

## Directory Contents

| File | Description |
|------|-------------|
| `README.md` | This documentation |
| `AGENTS.md` | Agent coordination guide |
| `SPEC.md` | Technical specification |



## Testing

```bash
uv run python -m pytest src/codomyrmex/tests/ -k ide -v
```

## Related Modules

- [Exceptions](../exceptions/README.md)

## Navigation

- **Source**: [src/codomyrmex/ide/](../../../src/codomyrmex/ide/)
- **Parent**: [Modules](../README.md)
