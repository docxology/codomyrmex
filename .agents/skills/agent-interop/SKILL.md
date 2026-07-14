---
name: agent-interop
description: Keep Codex, Claude Code, and Hermes workflows aligned through portable skills, explicit runtime adapters, and shared MCP contracts.
---

# Agent Interoperability

Treat `.agents/skills/` as the portable, repository-scoped skill layer. Keep runtime-specific configuration in the runtime’s own file and link back to the portable skill instead of duplicating its logic.

- Codex discovers project skills from `.agents/skills/` and project MCP settings from `.codex/config.toml`.
- Claude Code uses `.claude/skills/` and project MCP settings from `.mcp.json`; when a portable skill is not mirrored there, read the corresponding `.agents/skills/<name>/SKILL.md` explicitly.
- Hermes can discover the same tree through `skills.external_dirs` in `~/.hermes/config.yaml`; external skill directories are read-only discovery sources.
- Keep tool names, schemas, approval expectations, and verification steps in the shared documentation. Do not rely on one runtime’s permission model being honored by another.

When transferring work, pass objective, scope, assumptions, files changed, tool calls made, evidence, unresolved risks, and the next verification step. Prefer a small handoff record over copying hidden conversational state.
