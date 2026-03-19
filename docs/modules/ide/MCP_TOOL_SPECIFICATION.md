# IDE - MCP Tool Specification

Authoritative implementation: [`src/codomyrmex/ide/mcp_tools.py`](../../../src/codomyrmex/ide/mcp_tools.py).

## Antigravity backend

| Tool | Description |
|------|-------------|
| `codomyrmex.ide_get_active_file` | Active file heuristic for the Antigravity IDE relay. |
| `codomyrmex.ide_list_tools` | Lists tool names exposed by the Antigravity relay CLI. |

Responses include `"backend": "antigravity"`.

## Cursor backend

Filesystem-backed [`CursorClient`](../../../src/codomyrmex/ide/cursor/__init__.py) — not a live Cursor RPC.

| Tool | Description |
|------|-------------|
| `codomyrmex.ide_cursor_workspace_info` | Workspace path, connection flags, `.cursor` / `.cursorrules`, capabilities. |
| `codomyrmex.ide_cursor_get_active_file` | Mtime-based active file under the workspace. |
| `codomyrmex.ide_cursor_rules_read` | `.cursorrules` content with bounded length (`max_chars`). |

**Workspace resolution:** `workspace_path` → `CODOMYRMEX_CURSOR_WORKSPACE` → `cwd`.

See [Cursor integration](../../development/cursor-integration.md) for how this maps to the Cursor editor and repo layout.

## Navigation Links

- **Module docs**: [README.md](README.md)
- **Development**: [Cursor integration](../../development/cursor-integration.md)
- **Project root**: [../../../README.md](../../../README.md)
