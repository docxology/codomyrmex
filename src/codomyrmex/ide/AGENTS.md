# Agent Guidelines - IDE

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

## Module Overview

Programmatic integration with IDEs: Antigravity, Cursor, and VS Code.

## Key Classes

- **IDEClient** — Abstract base for all IDE integrations
- **CursorClient** — Cursor AI-first editor client
- **IDECommand** — Command with name, args, timeout
- **IDECommandResult** — Result with success, output, error
- **FileInfo** — File metadata (path, language, lines)

## Agent Instructions

1. **Connect before use** — Call `connect()` before executing commands
2. **Use safe execution** — Prefer `execute_command_safe()` for error handling
3. **Batch related commands** — Use `execute_batch()` for sequences
4. **Check success rate** — Monitor `get_success_rate()` for reliability
5. **Handle disconnects** — Catch `ConnectionError` and reconnect

## Common Patterns

```python
from codomyrmex.ide import CursorClient, IDECommand

client = CursorClient()
client.connect()

# Safe command execution
result = client.execute_command_safe("editor.action.formatDocument")
if not result.success:
    log.error(f"Format failed: {result.error}")

# Batch execution
commands = [
    IDECommand("editor.action.formatDocument"),
    IDECommand("workbench.action.files.save"),
]
results = client.execute_batch(commands)
```

## Testing Patterns

```python
# Verify connection
client = CursorClient()
assert client.connect()
assert client.is_connected()
assert client.status == IDEStatus.CONNECTED

# Verify command execution
result = client.execute_command_safe("test.command")
assert "success" in dir(result)
```

## Navigation

- [README](README.md) | [SPEC](SPEC.md) | [PAI](PAI.md)
