# IDE Integration — Functional Specification

**Module**: `codomyrmex.ide`  
**Version**: v0.1.0  
**Status**: Active

## 1. Overview

IDE Integration Module.

## 2. Architecture

### Components

| Component | Type | Description |
|-----------|------|-------------|
| `IDEStatus` | Class | Status of an IDE session. |
| `IDECommand` | Class | Represents an IDE command to be executed. |
| `IDECommandResult` | Class | Result of an IDE command execution. |
| `FileInfo` | Class | Information about a file in the IDE. |
| `IDEClient` | Class | Abstract base class for IDE integrations. |
| `to_dict()` | Function | to dict |
| `to_dict()` | Function | to dict |
| `to_dict()` | Function | to dict |
| `status()` | Function | Get the current connection status. |
| `command_history()` | Function | Get the history of executed commands. |

### Submodule Structure

- `antigravity/` — Antigravity IDE Integration
- `cursor/` — Cursor IDE Integration.
- `vscode/` — VS Code IDE Integration

## 3. Dependencies

See `src/codomyrmex/ide/__init__.py` for import dependencies.

## 4. Public API

```python
from codomyrmex.ide import IDEStatus, IDECommand, IDECommandResult, FileInfo, IDEClient
```

## 5. Testing

```bash
uv run python -m pytest src/codomyrmex/tests/ -k ide -v
```
