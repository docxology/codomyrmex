# AGENTS.md — `codomyrmex/.agents/skills/mcp-tool-use`

## Purpose

Portable repository-scoped skill: Use Model Context Protocol tools safely:
schema inspection, least-privilege selection, explicit approvals, bounded
execution, result verification. Defined entirely by [`SKILL.md`](SKILL.md).

## Key Files

- [`SKILL.md`](SKILL.md) — canonical definition: frontmatter
  (`name: mcp-tool-use`, `description`), a six-step workflow (inspect schemas and
  annotations → treat metadata as untrusted → smallest allow-list → show and
  approve sensitive calls → validate inputs and results → audit-log without
  secrets), and the Codomyrmex rule to prefer the read-only Codex allow-list.
- [`README.md`](README.md) — human signpost.

## Dependencies

- Claude Code wrapper: [`.claude/skills/mcp-tool-use/SKILL.md`](../../../.claude/skills/mcp-tool-use/SKILL.md)
  only points back to this file.
- Names [`.codex/config.toml`](../../../.codex/config.toml) as the default
  allow-list; that file starts
  [`run_mcp_server.py`](../../../scripts/model_context_protocol/run_mcp_server.py)
  with `--profile readonly`.
- Fourth step of the composition order in
  [docs/agents/agent-interoperability.md](../../../docs/agents/agent-interoperability.md),
  whose "Tool-use contract" section restates this workflow.
- Parent: [../AGENTS.md](../AGENTS.md)

## Development Guidelines

- Use whenever an MCP server or external tool is involved.
- This is the canonical copy; runtime wrappers such as
  `.claude/skills/mcp-tool-use/` stay pointers — change the workflow here.
- Keep the five-step tool-use contract in the interoperability doc consistent
  with this file when either changes.
- If the read-only tool set changes, update `.codex/config.toml` and
  `READONLY_TOOL_NAMES` in `run_mcp_server.py` together so this skill's
  guidance stays true.
