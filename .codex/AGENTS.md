# AGENTS.md — `codomyrmex/.codex`

## Purpose

Project-scoped configuration for the Codex agent runtime. It registers the
Codomyrmex MCP server for Codex with a read-only tool allow-list and
prompt-before-use approvals.

## Key Files

- [`config.toml`](config.toml) — a single `[mcp_servers.codomyrmex]` table that
  starts `scripts/model_context_protocol/run_mcp_server.py` through `uv run` with
  `--transport stdio --profile readonly`, sets `startup_timeout_sec = 20`,
  `tool_timeout_sec = 60`, and `default_tools_approval_mode = "prompt"`, and
  enables ten read-only tools (`git_status`, `git_diff`, `read_file`,
  `list_directory`, `search_code`, `analyze_python_file`, `json_query`,
  `checksum_file`, `list_modules`, `get_module_info`).
- [`README.md`](README.md) — human signpost.

## Dependencies

- [`scripts/model_context_protocol/run_mcp_server.py`](../scripts/model_context_protocol/run_mcp_server.py)
  is the server Codex launches; its `READONLY_TOOL_NAMES` set defines the
  `readonly` profile, so `enabled_tools` must stay a subset of it.
- Codex discovers project skills from [`.agents/skills/`](../.agents/skills/README.md);
  this file configures MCP only, and Codex applies it only to trusted projects.
- Referenced by [docs/agents/agent-interoperability.md](../docs/agents/agent-interoperability.md),
  [`.agents/skills/mcp-tool-use/SKILL.md`](../.agents/skills/mcp-tool-use/SKILL.md),
  and [`.agents/skills/agent-interop/SKILL.md`](../.agents/skills/agent-interop/SKILL.md).
- Parent: [../README.md](../README.md) · Root contract: [../AGENTS.md](../AGENTS.md)

## Development Guidelines

- Do not commit secrets or credentials into `config.toml`; keep secrets in the
  runtime's own credential store.
- Treat edits as behavior changes for any Codex-driven agent sessions.
- Keep the checked-in surface read-only: add a write or command tool only for a
  named task and restore the allow-list afterwards; do not switch the
  checked-in server to `--profile full`.
- Check what the server actually exposes before changing the allow-list:

  ```bash
  uv run python scripts/model_context_protocol/run_mcp_server.py --profile readonly --list-tools
  codex mcp list
  ```
