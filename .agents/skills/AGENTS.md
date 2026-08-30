# AGENTS.md — `codomyrmex/.agents/skills`

## Purpose
The canonical, repository-scoped portable skill library. Runtime adapters in
`.agent/skills/` and `.cursor/skills/` mirror or extend these.

## Layout
One folder per skill, each with a single `SKILL.md`:
`agent-interop`, `first-principles`, `mcp-tool-use`, `red-team`, `systems-thinking`.

## Gotchas
- Keep skill frontmatter (`name`, `description`) stable — runtimes index by it.
- New skills must be added to the crossover index (`.agent/SKILL_INDEX.md`).
