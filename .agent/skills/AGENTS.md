# AGENTS.md — `codomyrmex/.agent/skills`

## Purpose
Runtime-scoped skills for the `.agent` surface. Each child folder carries one `SKILL.md`.

## Layout
- `desloppify/` — codebase-quality skill driving the desloppify CLI: install, exclude noise, scan, then the next/resolve loop to raise the strict score. Triggered by /desloppify or tech-debt cleanup requests.

## Gotchas
- Prefer editing the `.agents/skills/` canonical copy when a skill exists there too;
  this tree is a runtime adapter, not the source of truth.
