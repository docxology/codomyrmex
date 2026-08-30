# AGENTS.md — `codomyrmex/.agents`

## Purpose
Repository-scoped, runtime-portable agent configuration: the canonical portable
skill library shared by Codex, Claude Code, Hermes, and other runtimes.

## Layout
- `skills/` — portable skills, each a folder with one `SKILL.md`.

## Gotchas
- This is the canonical copy for portable skills; `.agent/skills/` and
  `.cursor/skills/` hold runtime adapters. Edit here first, then mirror.
- Skills are referenced by name from `.agent/SKILL_INDEX.md` and
  `.cursor/skill_manifest.json`-style manifests — keep names stable.
