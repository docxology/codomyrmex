# Agent Guidelines - IDE

**Version**: v1.1.4 | **Status**: Active | **Last Updated**: March 2026

## Module Overview

Programmatic integration with IDEs: Antigravity, Cursor, and VS Code. Provides an abstract `IDEClient` base class that all IDE-specific clients implement, ensuring a consistent API for connection management, command execution, file operations, and event handling. Each submodule contains a concrete client: `AntigravityClient` for Google DeepMind's Antigravity IDE with artifact management, `CursorClient` for Cursor's AI-first editor with rules and model management, and `VSCodeClient` for VS Code with extension and settings management. The module tracks command history, success rates, and supports batch execution with configurable stop-on-error behavior.

## Key Files

| File | Purpose |
|------|---------|
| `__init__.py` | Exports `IDEClient`, `IDEStatus`, `IDECommand`, `IDECommandResult`, `FileInfo`, `CursorClient`, `VSCodeClient`, `AntigravityClient`; defines the abstract base class and shared data models |
| `antigravity/client.py` | `AntigravityClient` -- artifact management, conversation context, tool invocation, GUI automation via AppleScript, CLI chat integration |
| `cursor/__init__.py` | `CursorClient` -- `.cursorrules` management, AI model selection, workspace-based connection |
| `vscode/__init__.py` | `VSCodeClient` -- extension listing, workspace settings management, debug session control |

## Key Classes

- **IDEClient** -- Abstract base for all IDE integrations; defines `connect()`, `disconnect()`, `execute_command()`, `get_active_file()`, `open_file()`, `close_file()`, `get_open_files()`, `save_file()`, `save_all()`; provides `execute_command_safe()`, `execute_batch()`, `get_file_info()`, `get_success_rate()`
- **CursorClient** -- Cursor AI-first editor client with `get_rules()`, `update_rules()`, `get_models()`, `set_model()`
- **VSCodeClient** -- VS Code integration client with `list_extensions()`, `list_commands()`, `get_settings()`, `update_settings()`, `start_debug()`, `stop_debug()`
- **AntigravityClient** -- Antigravity IDE integration client with `list_artifacts()`, `get_artifact()`, `create_artifact()`, `update_artifact()`, `delete_artifact()`, `invoke_tool()`, `send_chat_message()`, `send_chat_gui()`
- **IDECommand** -- Dataclass representing a command with name, args, and timeout
- **IDECommandResult** -- Dataclass for command results with success, output, error, and execution_time
- **FileInfo** -- Dataclass for file metadata (path, name, is_modified, language, line_count)
- **IDEStatus** -- Enum with states: `DISCONNECTED`, `CONNECTING`, `CONNECTED`, `ERROR`

## Agent Instructions

1. **Connect before use** -- Call `connect()` before executing commands
2. **Use safe execution** -- Prefer `execute_command_safe()` for error handling
3. **Batch related commands** -- Use `execute_batch()` for sequences
4. **Check success rate** -- Monitor `get_success_rate()` for reliability
5. **Handle disconnects** -- Catch `ConnectionError` and reconnect
6. **Use the right client** -- Select `CursorClient`, `VSCodeClient`, or `AntigravityClient` based on the target IDE

## Operating Contracts

- `execute_command()` raises `CommandExecutionError` if the client is not connected
- `execute_command_safe()` never raises -- it catches all exceptions and returns an `IDECommandResult` with `success=False`
- `execute_batch()` stops on first failure by default (`stop_on_error=True`); set to `False` for best-effort execution
- `AntigravityClient.create_artifact()` raises `ArtifactError` if not connected or if `artifact_type` is invalid
- `AntigravityClient.update_artifact()` raises `ArtifactError` if the artifact does not exist
- `AntigravityClient.execute_command()` raises `CommandExecutionError` if the command is not in `AntigravityClient.TOOLS`
- `VSCodeClient.update_settings()` raises `IDEError` if not connected
- `VSCodeClient.start_debug()` and `stop_debug()` raise `IDEError` if not connected
- `CursorClient.update_rules()` raises `IDEError` if not connected
- `get_file_info()` returns `None` if the file does not exist on disk
- **DO NOT** call `execute_command()` without first calling `connect()` -- always check `is_connected()` or handle the exception
- **DO NOT** access `_command_history` directly -- use `command_history` (property returns a copy), `get_last_command()`, or `get_success_rate()`

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
| **Researcher** | Read-only | Inspect capabilities via `get_capabilities()`, review command history | SAFE |

### Engineer Agent
**Use Cases**: Integrates IDE features including Cursor and Antigravity clients, executes editor commands, manages batch operations, and monitors connection reliability.

### Architect Agent
**Use Cases**: Reviews IDE plugin architecture, evaluates client abstraction layers, and assesses command execution patterns across editor integrations.

### QATester Agent
**Use Cases**: Validates IDE integration behavior including connection lifecycle, command execution success rates, batch operation ordering, and error recovery.

### Researcher Agent
**Use Cases**: Inspects IDE capabilities and feature sets via `get_capabilities()`, reviews command execution history for analysis and documentation.

## Navigation

- [README](README.md) | [SPEC](SPEC.md) | [PAI](PAI.md)
