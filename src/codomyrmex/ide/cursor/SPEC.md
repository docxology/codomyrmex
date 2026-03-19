# cursor - Functional Specification

**Version**: v0.2.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose

Provide a deterministic, testable Cursor integration that implements the shared `IDEClient` contract.  
The current scope is local workspace automation (rules, model state, file-state inspection, and command routing), not remote Cursor APIs.

## Functional Scope

### Connection Lifecycle

- `connect()`:
  - Sets status to `CONNECTING`.
  - Connects when workspace exists or Cursor markers are present (`.cursor` or `.cursorrules`).
  - Sets status to `CONNECTED` on success, `ERROR` on failure.
- `disconnect()`:
  - Sets status to `DISCONNECTED`.
  - Clears tracked open-file state.

### File Operations

- Source-file discovery scans recursively in workspace and ignores hidden directories.
- `get_active_file()` returns the most recently modified source/config file.
- `open_file()` tracks opened file paths if they exist.
- `get_open_files()` returns tracked files when available, otherwise a bounded workspace fallback.

### Rules Management

- `.cursorrules` read/write is UTF-8.
- `update_rules()` accepts:
  - Raw string content.
  - Dict content (serialized to JSON).
- Rules updates require active connection.

### Model State

- `get_models()` returns known model list.
- `set_model()` updates active model only for known entries.
- Capabilities include `active_model`.

### Command Routing

`execute_command()` supports only explicit command names and raises `CommandExecutionError` for unknown commands:

- `cursor.rules.get`
- `cursor.rules.update`
- `cursor.model.get`
- `cursor.model.set`
- `cursor.file.open`
- `cursor.file.close`
- `cursor.file.list_open`

## Interface Contract

```python
class CursorClient(IDEClient):
    def connect(self) -> bool: ...
    def disconnect(self) -> None: ...
    def is_connected(self) -> bool: ...
    def get_capabilities(self) -> dict[str, Any]: ...
    def execute_command(self, command: str, args: dict | None = None) -> Any: ...
    def get_active_file(self) -> str | None: ...
    def open_file(self, path: str) -> bool: ...
    def close_file(self, path: str) -> bool: ...
    def get_open_files(self) -> list[str]: ...
    def save_file(self, path: str) -> bool: ...
    def save_all(self) -> bool: ...
    def get_rules(self) -> dict[str, Any]: ...
    def update_rules(self, rules: dict[str, Any]) -> bool: ...
    def get_models(self) -> list[str]: ...
    def set_model(self, model: str) -> bool: ...
```

## Validation

Primary validation is through unit tests under `src/codomyrmex/tests/unit/ide/`.

## Navigation

- **Human Documentation**: [README.md](README.md)
- **Agent Documentation**: [AGENTS.md](AGENTS.md)
- **Parent Module**: [ide](../README.md)
