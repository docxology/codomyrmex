# AGENTS.md — `codomyrmex/.agents/skills/red-team`

## Purpose
Portable repository-scoped skill: Adversarially test a design, implementation, agent workflow, or tool surface for realistic failure and abuse paths within authorized scope. Defined entirely by [`SKILL.md`](SKILL.md).

## Layout
- `SKILL.md` — the skill definition (frontmatter: name, description).

## Gotchas
- Use for security, reliability, permission, and prompt-injection review.
- Runtime adapters (`.cursor/skills/`, `.agent/skills/`) may mirror this skill; edit the canonical copy here first.
