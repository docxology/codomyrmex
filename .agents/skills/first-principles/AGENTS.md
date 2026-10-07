# AGENTS.md — `codomyrmex/.agents/skills/first-principles`

## Purpose

Portable repository-scoped skill: Reduce an ambiguous technical problem to
verified facts, constraints, and explicit decisions before proposing a
solution. Defined entirely by [`SKILL.md`](SKILL.md).

## Key Files

- [`SKILL.md`](SKILL.md) — canonical definition: frontmatter
  (`name: first-principles`, `description`), a six-step workflow (outcome →
  separate facts from assumptions → decompose → verify decision-changing facts →
  rebuild → record trade-offs), and the required decision-record output
  (objective, facts, constraints, assumptions, options, chosen design, risks,
  verification evidence).
- [`README.md`](README.md) — human signpost.

## Dependencies

- Claude Code wrapper: [`.claude/skills/first-principles/SKILL.md`](../../../.claude/skills/first-principles/SKILL.md)
  only points back to this file.
- Codex discovers it from `.agents/skills/`; Hermes via `skills.external_dirs`.
- First step of the composition order in
  [docs/agents/agent-interoperability.md](../../../docs/agents/agent-interoperability.md);
  its decision record feeds `systems-thinking`.
- Parent: [../AGENTS.md](../AGENTS.md)

## Development Guidelines

- Use when a request is ambiguous or a design has accumulated unexamined assumptions.
- This is the canonical copy; runtime wrappers such as
  `.claude/skills/first-principles/` stay pointers — change the workflow here.
- Keep `name` equal to the folder name; a rename must also update the wrapper,
  `.agent/SKILL_INDEX.md`, and the interoperability doc.
- Preserve the rule that an assumption is never presented as a fact, and keep
  the decision-record fields stable so downstream skills can rely on them.
