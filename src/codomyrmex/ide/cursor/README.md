# Cursor IDE Integration

**Version**: v0.2.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

`codomyrmex.ide.cursor` provides a concrete `IDEClient` implementation for Cursor workspaces.  
It focuses on filesystem-backed behavior that can be validated locally: connection lifecycle, source file discovery, `.cursorrules` management, model selection, and command routing.

## Public API

### Core Class

- `CursorClient` — Cursor-specific implementation of `IDEClient`.

### Main Methods

- `connect() -> bool` — Connects to a workspace and sets IDE status.
- `disconnect() -> None` — Disconnects and clears tracked open-file state.
- `get_capabilities() -> dict[str, Any]` — Returns supported features, commands, models, active model, status, and workspace path.
- `execute_command(command: str, args: dict | None = None) -> Any` — Executes supported Cursor commands.
- `get_active_file() -> str | None` — Returns most recently modified source/config file in the workspace.
- `get_open_files() -> list[str]` — Returns tracked open files or a deterministic fallback list.
- `get_rules() -> dict[str, Any]` / `update_rules(rules: dict[str, Any]) -> bool` — Reads/writes `.cursorrules`.
- `get_models() -> list[str]` / `set_model(model: str) -> bool` — Model list and active-model selection.

## Supported Commands

- `cursor.rules.get`
- `cursor.rules.update`
- `cursor.model.get`
- `cursor.model.set`
- `cursor.file.open`
- `cursor.file.close`
- `cursor.file.list_open`

## MCP bridge

When MCP is enabled, Cursor workspace introspection is also exposed as tools (see parent [MCP_TOOL_SPECIFICATION.md](../MCP_TOOL_SPECIFICATION.md)):

- `codomyrmex.ide_cursor_workspace_info`
- `codomyrmex.ide_cursor_get_active_file`
- `codomyrmex.ide_cursor_rules_read`

Optional env: `CODOMYRMEX_CURSOR_WORKSPACE` if the MCP server cwd is not the repo root.

## Verification

```bash
uv run pytest src/codomyrmex/tests/unit/ide/test_cursor_impl.py
uv run pytest src/codomyrmex/tests/unit/ide/test_cursor_settings.py
uv run pytest src/codomyrmex/tests/unit/ide/test_ide_mcp_tools.py
```

## Navigation

- **Agent Guide**: [AGENTS.md](AGENTS.md)
- **Specification**: [SPEC.md](SPEC.md)
- **PAI Context**: [PAI.md](PAI.md)
- **Parent Module**: [ide](../README.md)
