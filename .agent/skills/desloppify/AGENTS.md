# AGENTS.md — `codomyrmex/.agent/skills/desloppify`

## Purpose
Runtime adapter for the desloppify skill (Claude Code surface): drives the
desloppify CLI to raise codebase strict score — install, exclude noise, scan,
then the next/resolve loop.

## Layout
- `SKILL.md` — the skill definition (trigger: /desloppify, tech-debt cleanup, strict score, codebase health scanning).

## Gotchas
- Adapter copy; edit the canonical definition (`.agents/skills/` or `.cursor/skills/desloppify/`) first and mirror here.
