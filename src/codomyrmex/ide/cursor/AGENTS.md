# Cursor - Agent Coordination

## Purpose

Integration with the Cursor AI-first code editor, providing programmatic access to workspace connection, `.cursorrules` management, model selection, and command execution.

## Key Components

| Component | Role |
|-----------|------|
| `CursorClient` | `IDEClient` subclass for Cursor IDE interaction |

## Operating Contracts

- `connect()` returns `True` if `.cursor/` dir, `.cursorrules` file, or workspace path exists.
- `get_active_file()` scans workspace root (non-recursive) for the most recently modified source file across 30+ extensions.
- `get_rules()` reads and returns `.cursorrules` file content; returns `{"exists": False}` if absent.
- `update_rules()` writes content to `.cursorrules`; accepts string or dict (auto-serialized to JSON).
- `get_capabilities()` returns static model list: gpt-4, gpt-4-turbo, gpt-3.5-turbo, claude-3-opus, claude-3-sonnet.
- `execute_command()` raises `CommandExecutionError` if not connected.

## Integration Points

- **Parent module**: `ide/` provides the `IDEClient` abstract base class and shared exceptions (`IDEError`, `ConnectionError`, `CommandExecutionError`).
- **Workspace**: Operates on the filesystem at `workspace_path` (defaults to `cwd()`).

## Navigation

- **Parent**: [ide/](../README.md)
- **Sibling**: [SPEC.md](SPEC.md)
- **Root**: [/README.md](../../../../README.md)
