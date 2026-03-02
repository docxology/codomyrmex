# Agent Guidelines - IDE

**Version**: v1.0.5 | **Status**: Active | **Last Updated**: March 2026

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

## PAI Agent Role Access Matrix

| PAI Agent | Access Level | Primary Capabilities | Trust Level |
|-----------|-------------|---------------------|-------------|
| **Engineer** | Full | Direct Python import, class instantiation, full API access | TRUSTED |
| **Architect** | Read + Design | API review, interface design, dependency analysis | OBSERVED |
| **QATester** | Validation | Integration testing via pytest, output validation | OBSERVED |

### Engineer Agent
**Use Cases**: Integrates IDE features including Cursor and Antigravity clients, executes editor commands, manages batch operations, and monitors connection reliability.

### Architect Agent
**Use Cases**: Reviews IDE plugin architecture, evaluates client abstraction layers, and assesses command execution patterns across editor integrations.

### QATester Agent
**Use Cases**: Validates IDE integration behavior including connection lifecycle, command execution success rates, batch operation ordering, and error recovery.

## Navigation

- [README](README.md) | [SPEC](SPEC.md) | [PAI](PAI.md)
