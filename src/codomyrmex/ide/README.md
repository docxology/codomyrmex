# IDE Module

**Version**: v0.1.0 | **Status**: Active

Programmatic integration with IDEs: Antigravity, Cursor, and VS Code.

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

## Navigation

- [SPEC](SPEC.md) | [AGENTS](AGENTS.md) | [PAI](PAI.md)
