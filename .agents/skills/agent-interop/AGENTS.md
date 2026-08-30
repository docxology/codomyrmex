# AGENTS.md — `codomyrmex/.agents/skills/agent-interop`

## Purpose
Portable repository-scoped skill: Keep Codex, Claude Code, and Hermes workflows aligned through portable skills, explicit runtime adapters, and shared MCP contracts. Defined entirely by [`SKILL.md`](SKILL.md).

## Layout
- `SKILL.md` — the skill definition (frontmatter: name, description).

## Gotchas
- Treat `.agents/skills/` as the portable, repository-scoped skill library; mirror into runtime-specific folders rather than forking content.
- Runtime adapters (`.cursor/skills/`, `.agent/skills/`) may mirror this skill; edit the canonical copy here first.
