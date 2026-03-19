# IDE - MCP Tool Specification

This document describes MCP tools exposed by the `ide` module. They are discovered via `@mcp_tool` in [`mcp_tools.py`](mcp_tools.py).

## Antigravity backend

| Tool | Description |
|------|-------------|
| `codomyrmex.ide_get_active_file` | Active file heuristic for the Antigravity IDE relay. |
| `codomyrmex.ide_list_tools` | Lists tool names exposed by the Antigravity relay CLI. |

Responses include `"backend": "antigravity"` for disambiguation.

## Cursor backend

These tools use [`codomyrmex.ide.cursor.CursorClient`](cursor/__init__.py): filesystem-backed workspace state, not a live Cursor RPC. They are suitable for agents that need a consistent view of `.cursorrules`, workspace layout, and mtime-based “active file” hints.

| Tool | Description |
|------|-------------|
| `codomyrmex.ide_cursor_workspace_info` | Connection status, resolved workspace path, `.cursor` / `.cursorrules` presence, capability metadata. |
| `codomyrmex.ide_cursor_get_active_file` | Most recently modified source/config file under the workspace (same heuristic as `CursorClient.get_active_file`). |
| `codomyrmex.ide_cursor_rules_read` | Reads `.cursorrules` with a bounded payload (`max_chars`, clamped 1–512_000). |

**Workspace resolution** (all Cursor tools):

1. `workspace_path` argument if provided  
2. Else `CODOMYRMEX_CURSOR_WORKSPACE`  
3. Else process current working directory  

Responses include `"backend": "cursor"`.

## Python usage

```python
from codomyrmex.ide.mcp_tools import ide_cursor_workspace_info, ide_get_active_file

ide_get_active_file()
ide_cursor_workspace_info(workspace_path="/path/to/repo")
```

## Navigation Links

- **Parent**: [ide README](README.md)
- **API**: [API_SPECIFICATION.md](API_SPECIFICATION.md)
- **Cursor submodule**: [cursor/README.md](cursor/README.md)
- **Project root**: [../../../README.md](../../../README.md)
