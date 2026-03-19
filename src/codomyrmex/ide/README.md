# ide

**Version**: v0.2.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

Unified IDE automation: abstract [`IDEClient`](__init__.py) with concrete backends for **Cursor**, **VS Code**, and **Antigravity**. Submodules live under `cursor/`, `vscode/`, and `antigravity/`.

## MCP tools

[`mcp_tools.py`](mcp_tools.py) registers discrete MCP tools (auto-discovered by the Codomyrmex MCP bridge):

- **Antigravity:** `ide_get_active_file`, `ide_list_tools`
- **Cursor:** `ide_cursor_workspace_info`, `ide_cursor_get_active_file`, `ide_cursor_rules_read`

Specification: [MCP_TOOL_SPECIFICATION.md](MCP_TOOL_SPECIFICATION.md). Editor-focused guide: [docs/development/cursor-integration.md](../../../docs/development/cursor-integration.md).

## Documentation

| Doc | Purpose |
|-----|---------|
| [API_SPECIFICATION.md](API_SPECIFICATION.md) | `IDEClient` contract |
| [MCP_TOOL_SPECIFICATION.md](MCP_TOOL_SPECIFICATION.md) | Tool names, parameters, backends |
| [SPEC.md](SPEC.md) | Module design |
| [PAI.md](PAI.md) | Agent integration notes |
| [AGENTS.md](AGENTS.md) | Directory index for agents |

## Verification

```bash
uv run pytest src/codomyrmex/tests/unit/ide/
```

## Navigation

- **Parent**: [codomyrmex](../README.md)
- **Project root**: [../../../README.md](../../../README.md)
