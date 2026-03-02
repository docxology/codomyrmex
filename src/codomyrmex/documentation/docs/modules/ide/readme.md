# IDE Integration Module

**Version**: v1.0.5 | **Status**: Active | **Last Updated**: March 2026

Programmatic integration with IDEs: Antigravity, Cursor, and VS Code.

## PAI Integration

| Algorithm Phase | Role | Tools Used |
|----------------|------|-----------|
| **BUILD** | Code editing operations via IDE command execution | Direct Python import |
| **EXECUTE** | IDE integrations for automated formatting and saves | Direct Python import |
| **OBSERVE** | IDE state inspection including open files and status | Direct Python import |

PAI agents access this module via direct Python import through the MCP bridge. The Engineer agent drives IDE commands during BUILD for automated code editing, and inspects IDE state during OBSERVE to understand the current workspace context.

## Installation

```bash
uv add codomyrmex
```

Or for development:

```bash
uv sync
```

## Key Exports

### Classes
- **`IDEStatus`** — Status of an IDE session.
- **`IDECommand`** — Represents an IDE command to be executed.
- **`IDECommandResult`** — Result of an IDE command execution.
- **`FileInfo`** — Information about a file in the IDE.
- **`IDEClient`** — Abstract base class for IDE integrations.

### Submodules
- **`antigravity/`** — Antigravity IDE Integration
- **`cursor/`** — Cursor IDE Integration.
- **`vscode/`** — VS Code IDE Integration

## Quick Start

```python
from codomyrmex.ide import (
    IDEClient, CursorClient, IDECommand, IDECommandResult, FileInfo
)

# Connect to Cursor IDE
client = CursorClient()
client.connect()

# Execute commands
client.execute_command("editor.action.formatDocument")
result = client.execute_command_safe("workbench.action.files.save")
print(f"Success: {result.success}, Time: {result.execution_time:.2f}s")

# Get file information
active = client.get_active_file()
files = client.get_open_files()
info = client.get_file_info(active)
print(f"Language: {info.language}, Lines: {info.line_count}")

# Batch execution
commands = [
    IDECommand("editor.action.formatDocument"),
    IDECommand("workbench.action.files.save"),
]
results = client.execute_batch(commands, stop_on_error=True)

# Event handling
client.register_event_handler("file_saved", on_file_saved)

client.disconnect()
```

## Exports

| Class | Description |
|-------|-------------|
| `IDEClient` | Abstract base class for IDE integrations |
| `CursorClient` | Cursor AI-first editor client |
| `IDEStatus` | Enum: disconnected, connecting, connected, error |
| `IDECommand` | Command with name, args, timeout |
| `IDECommandResult` | Result with success, output, execution_time |
| `FileInfo` | File path, name, language, line_count |
| `IDEError` | Base IDE exception |
| `ConnectionError` | Connection failure |
| `CommandExecutionError` | Command execution failure |

## Submodules

- `antigravity/` — Google DeepMind Antigravity integration
- `cursor/` — Cursor AI editor integration
- `vscode/` — Visual Studio Code integration

## Testing

```bash
uv run python -m pytest src/codomyrmex/tests/ -k ide -v
```

## Documentation

- [Module Documentation](../../../docs/modules/ide/README.md)
- [Agent Guide](../../../docs/modules/ide/AGENTS.md)
- [Specification](../../../docs/modules/ide/SPEC.md)

## Navigation

- [SPEC](SPEC.md) | [AGENTS](AGENTS.md) | [PAI](PAI.md)
