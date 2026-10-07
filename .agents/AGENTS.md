# AGENTS.md — `codomyrmex/.agents`

## Purpose

Repository-scoped, runtime-portable agent configuration: the canonical portable
skill library shared by Codex, Claude Code, Hermes, and other runtimes.

## Key Files

- [`skills/`](skills/README.md) — five portable skills (`agent-interop`,
  `first-principles`, `mcp-tool-use`, `red-team`, `systems-thinking`), each a
  folder with one `SKILL.md`.
- [`README.md`](README.md) — human signpost listing each skill's purpose.

## Dependencies

- Codex discovers project skills directly from `.agents/skills/`.
- Claude Code reaches them through thin pointer wrappers in
  `.claude/skills/<name>/SKILL.md` (for example
  [`.claude/skills/agent-interop/SKILL.md`](../.claude/skills/agent-interop/SKILL.md)).
- Hermes reads the tree as a read-only `skills.external_dirs` entry
  ([example config](../config/hermes_external_skills.example.yaml)).
- Listed in [`.agent/SKILL_INDEX.md`](../.agent/SKILL_INDEX.md) and described in
  [docs/agents/agent-interoperability.md](../docs/agents/agent-interoperability.md).
- Parent: [../README.md](../README.md) · Root contract: [../AGENTS.md](../AGENTS.md)

## Development Guidelines

- This is the canonical copy for portable skills: edit workflow content here and
  keep runtime wrappers as pointers rather than forks.
- Skills are referenced by name from `.claude/skills/`, `.agent/SKILL_INDEX.md`,
  and the interoperability doc — keep names stable, and update all of them
  together when a skill is added, renamed, or removed.
- Keep runtime-specific settings (MCP servers, approvals) in each runtime's own
  file, such as [`.codex/config.toml`](../.codex/config.toml), not in this tree.
