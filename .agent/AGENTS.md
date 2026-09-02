# AGENTS.md — `codomyrmex/.agent`

## Purpose
Runtime-local agent configuration for the Claude Code / Antigravity crossover:
a skill index, runtime-scoped skills, and workflow definitions.

## Layout
- `SKILL_INDEX.md` — index of all Claude Code plugins and their `SKILL.md` paths; Antigravity reads any skill on demand via `view_file`.
- `skills/` — runtime-scoped skills (currently `desloppify`).
- `workflows/` — workflow definitions consumed by agent runtimes.

## Gotchas
- Runtime-scoped skills here are adapters; the portable repository-scoped set
  lives in `.agents/skills/`. Keep `SKILL_INDEX.md` in sync when either set changes.

## Key Files
- `README.md`: Readme file

## Dependencies
- None

## Development Guidelines
- Follow standard practices
