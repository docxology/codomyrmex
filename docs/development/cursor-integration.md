# Cursor editor and Codomyrmex

This repo is often opened in **Cursor**. These are the supported integration paths between the editor and Codomyrmex.

**MCP errors (`spawn uv ENOENT`, `spawn codex ENOENT`, `No server info found`):** see [cursor-mcp-troubleshooting.md](cursor-mcp-troubleshooting.md). Extensions such as **Second Opinion / Codex** spawn `codex mcp-server`; that requires the [Codex CLI](https://developers.openai.com/codex/cli/) installed and discoverable (often an absolute path or symlink).

## Rules and project context

- **Native Cursor rules (committed)**: [`.cursor/rules/`](../../.cursor/rules/) — `.mdc` files with frontmatter; see [`.cursor/README.md`](../../.cursor/README.md). Root `.gitignore` keeps **`rules/`** and **`README.md`** under `.cursor/` tracked; other paths under `.cursor/` stay ignored.
- **Legacy fragments**: [`cursorrules/general.cursorrules`](../../cursorrules/general.cursorrules) and [`cursorrules/codomyrmex-cursor.cursorrules`](../../cursorrules/codomyrmex-cursor.cursorrules) — same policies in plain text for reference or other tools.

## Cursor global `mcp.json` (full tool surface)

To attach **all** PAI-bridge tools (static + auto-discovered module tools, resources, prompts), add a server entry to **Cursor → Settings → MCP** or edit `~/.cursor/mcp.json`:

1. Copy [cursor-mcp.json.example](cursor-mcp.json.example).
2. Replace `/ABSOLUTE/PATH/TO/codomyrmex` with your clone path (repo root where `pyproject.toml` lives). The example includes an optional **`codex`** server using `/opt/homebrew/bin/codex` (Apple Silicon); run `which codex` and edit that path (e.g. `/usr/local/bin/codex` on some Intel Homebrew installs).
3. Run **`uv sync`** once so **`.venv/bin/python`** exists — the example uses that interpreter so Cursor does not need `uv` on **PATH** (macOS GUI apps often lack `~/.local/bin`, which causes `spawn uv ENOENT`).
4. **`cwd`** must be the repo root so `scripts/model_context_protocol/run_pai_mcp_stdio.py` resolves.
5. **`CODOMYRMEX_CURSOR_WORKSPACE`** aligns `ide_cursor_*` MCP helpers with the repo when needed.

**Optional:** If you prefer `uv run`, set `"command"` to the **absolute** path from `which uv` (e.g. `/Users/you/.local/bin/uv`) — not the bare name `uv`.

**Command** (from repo root, smoke — should print tool count then block on stdin; Ctrl+C to exit):

```bash
uv run python -c "from codomyrmex.agents.pai.mcp.server import create_codomyrmex_mcp_server; s=create_codomyrmex_mcp_server(transport='stdio'); print('tools', s.tool_count)"
```

**stdio runner** (what Cursor invokes): [`scripts/model_context_protocol/run_pai_mcp_stdio.py`](../../scripts/model_context_protocol/run_pai_mcp_stdio.py)

**Bidirectional MCP checks** (request/response same as newline JSON-RPC over stdio):

```bash
uv run pytest src/codomyrmex/tests/integration/pai/test_mcp_stdio_bidirectional.py::test_pai_mcp_inprocess_jsonrpc_bidirectional --no-cov -q
uv run pytest src/codomyrmex/tests/integration/pai/test_mcp_stdio_bidirectional.py::test_pai_mcp_stdio_subprocess_bidirectional_roundtrip --no-cov -q
```

The subprocess test drives a real `uv run` child and skips non-JSON stdout lines before parsing (logging may appear ahead of MCP payloads).

## MCP (PAI / Codomyrmex bridge)

When Codomyrmex MCP is enabled, the `ide` module exposes Cursor-oriented tools (namespaced `codomyrmex.*`):

| Tool | Role |
|------|------|
| `ide_cursor_workspace_info` | Workspace root, `.cursor` / `.cursorrules` presence, capability list |
| `ide_cursor_get_active_file` | Mtime-based “active” source file under the workspace |
| `ide_cursor_rules_read` | Read `.cursorrules` with a size cap |

Antigravity-specific tools remain: `ide_get_active_file`, `ide_list_tools`.

**Workspace root for Cursor tools:** set `CODOMYRMEX_CURSOR_WORKSPACE` to the repo root when the MCP server’s cwd differs from the project (e.g. multi-root or wrapper processes). Otherwise tools default to the server process cwd.

Details: [`src/codomyrmex/ide/MCP_TOOL_SPECIFICATION.md`](../../src/codomyrmex/ide/MCP_TOOL_SPECIFICATION.md).

## Python API

`CursorClient` lives in `codomyrmex.ide.cursor`. See [`src/codomyrmex/ide/cursor/README.md`](../../src/codomyrmex/ide/cursor/README.md).

## Commands and tests

```bash
uv sync
# Cursor MCP tools + metadata + committed `.cursor/rules/` layout
uv run pytest src/codomyrmex/tests/unit/ide/test_ide_mcp_tools.py --no-cov -q
# Full IDE surface (Cursor client, Antigravity client, MCP, helpers)
uv run pytest \
  src/codomyrmex/tests/unit/ide/test_ide_mcp_tools.py \
  src/codomyrmex/tests/unit/ide/test_cursor_settings.py \
  src/codomyrmex/tests/unit/ide/test_cursor_impl.py \
  src/codomyrmex/tests/unit/ide/test_ide.py \
  src/codomyrmex/tests/unit/ide/test_ide_common.py \
  src/codomyrmex/tests/unit/ide/test_tool_provider.py \
  --no-cov -q
```

Smoke (optional):

```bash
uv run python -c "from codomyrmex.ide.mcp_tools import ide_cursor_workspace_info; import tempfile; from pathlib import Path; d=tempfile.mkdtemp(); Path(d,'f.py').write_text('1'); print(ide_cursor_workspace_info(workspace_path=d))"
```

## Navigation

- [Environment setup](environment-setup.md)
- [Testing strategy](testing-strategy.md)
- [Documentation hub](../README.md)
