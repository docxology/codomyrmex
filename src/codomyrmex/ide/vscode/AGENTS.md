# Codomyrmex Agents — src/codomyrmex/ide/vscode

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose

VS Code IDE integration providing programmatic access to workspace management,
extension listing, settings read/write, command execution, and debug session
control. Implements the `IDEClient` abstract base from `codomyrmex.ide`.

## Key Components

| File | Class / Function | Role |
|------|-----------------|------|
| `__init__.py` | `VSCodeClient` | Full IDEClient implementation for VS Code |
| `__init__.py` | `VSCodeClient.connect()` | Detect VS Code workspace via `.vscode/` dir or `*.code-workspace` files |
| `__init__.py` | `VSCodeClient.execute_command()` | Execute VS Code command IDs (e.g., `editor.action.formatDocument`) |
| `__init__.py` | `VSCodeClient.get_settings()` | Read `.vscode/settings.json`, parse as JSON |
| `__init__.py` | `VSCodeClient.update_settings()` | Merge and write `.vscode/settings.json` |
| `__init__.py` | `VSCodeClient.list_extensions()` | Return installed extension metadata list |
| `__init__.py` | `VSCodeClient.start_debug()` / `stop_debug()` | Guard debug session start/stop behind connection check |

## Operating Contracts

- All mutating methods (`execute_command`, `update_settings`, `start_debug`, `stop_debug`) raise `IDEError` or `CommandExecutionError` if not connected — no silent no-ops.
- `connect()` succeeds whenever `workspace_path` exists, even without a `.vscode/` directory.
- Settings updates merge with existing settings; never overwrite without reading first via `get_settings()`.
- Errors during JSON parsing in `get_settings()` are logged via `logging.getLogger` and re-raised — no silent empty-dict fallbacks.
- Raises `IDEError` (from `codomyrmex.ide`) for session-level failures; `CommandExecutionError` for command dispatch failures.

## Integration Points

- **Depends on**: `codomyrmex.ide` (`IDEClient`, `IDEError`, `CommandExecutionError`, `ConnectionError`)
- **Used by**: `codomyrmex.ide` package (as the `vscode` provider), agents needing VS Code workspace automation

## Navigation

- **📁 Parent**: [ide](../README.md)
- **🏠 Root**: ../../../../README.md
