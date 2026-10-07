# AGENTS.md — `codomyrmex/.agent/skills`

## Purpose

Runtime-scoped skills for the `.agent` surface. Each child folder carries one
`SKILL.md`. Skills that also exist in the portable library live canonically in
`.agents/skills/`; skills that exist only here (currently `desloppify`) are
canonical here.

## Key Files

- [`desloppify/`](desloppify/SKILL.md) — codebase-quality skill driving the
  desloppify CLI: install, exclude noise, scan, then the next/resolve loop to
  raise the strict score. Triggered by /desloppify or tech-debt cleanup requests.
- [`README.md`](README.md) — human signpost.

## Dependencies

- [`scripts/skills/skill_utils.py`](../../scripts/skills/skill_utils.py) searches
  this directory first (`list`, `show`) and scaffolds new skills here by default
  (`create <name>`).
- [`../workflows/desloppify.md`](../workflows/desloppify.md) and
  [`.cursor/skills/desloppify/SKILL.md`](../../.cursor/skills/desloppify/SKILL.md)
  both point at `desloppify/SKILL.md` instead of copying it.
- Indexed from [`../SKILL_INDEX.md`](../SKILL_INDEX.md); portable skills:
  [`.agents/skills/`](../../.agents/skills/README.md).
- Parent: [../AGENTS.md](../AGENTS.md)

## Development Guidelines

- Prefer editing the `.agents/skills/` canonical copy when a skill exists there
  too; for skills that exist only here, this tree is the source of truth and
  other runtimes should point to it.
- A skill scaffolded with `skill_utils.py create` contains template text
  (`version: 0.1.0`, generic steps); replace all of it before committing.
- Give every new skill folder a `README.md`/`AGENTS.md` pair and an entry in
  `../SKILL_INDEX.md`.
