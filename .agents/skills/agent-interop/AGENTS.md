# AGENTS.md — `codomyrmex/.agents/skills/agent-interop`

## Purpose

Portable repository-scoped skill: Keep Codex, Claude Code, and Hermes workflows
aligned through portable skills, explicit runtime adapters, and shared MCP
contracts. Defined entirely by [`SKILL.md`](SKILL.md).

## Key Files

- [`SKILL.md`](SKILL.md) — canonical definition: frontmatter
  (`name: agent-interop`, `description`), where each runtime discovers skills and
  MCP settings, and the handoff record fields (objective, scope, assumptions,
  files changed, tool calls, evidence, unresolved risks, next verification step).
- [`README.md`](README.md) — human signpost.

## Dependencies

- Claude Code wrapper: [`.claude/skills/agent-interop/SKILL.md`](../../../.claude/skills/agent-interop/SKILL.md)
  only points back to this file.
- Runtime files it names: [`.codex/config.toml`](../../../.codex/config.toml)
  (Codex MCP), a project `.mcp.json` for Claude Code (opt-in from
  [`config/claude_code_mcp.example.json`](../../../config/claude_code_mcp.example.json)),
  and `~/.hermes/config.yaml` (from
  [`config/hermes_external_skills.example.yaml`](../../../config/hermes_external_skills.example.yaml)).
- Final step of the composition order in
  [docs/agents/agent-interoperability.md](../../../docs/agents/agent-interoperability.md).
- Parent: [../AGENTS.md](../AGENTS.md)

## Development Guidelines

- Treat `.agents/skills/` as the portable, repository-scoped skill library;
  mirror into runtime-specific folders rather than forking content.
- This is the canonical copy; runtime wrappers such as
  `.claude/skills/agent-interop/` stay pointers — change the workflow here.
- When a runtime changes where it reads skills or MCP settings, update this
  file and the "Runtime setup" section of the interoperability doc together.
- Do not encode one runtime's permission model as if another runtime honors it.
