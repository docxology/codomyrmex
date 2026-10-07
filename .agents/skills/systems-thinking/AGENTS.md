# AGENTS.md — `codomyrmex/.agents/skills/systems-thinking`

## Purpose

Portable repository-scoped skill: Analyze a change as part of a wider system:
boundaries, dependencies, feedback loops, delays, incentives, leverage points.
Defined entirely by [`SKILL.md`](SKILL.md).

## Key Files

- [`SKILL.md`](SKILL.md) — canonical definition: frontmatter
  (`name: systems-thinking`, `description`), a six-step workflow (boundary and
  owners → stocks, flows, and state transitions → dependencies and feedback
  loops → second-order effects → high-leverage interventions → indicators,
  guardrails, and rollback), and the required output (causal map or table,
  intervention, downstream effects, risks, measurements).
- [`README.md`](README.md) — human signpost.

## Dependencies

- Claude Code wrapper: [`.claude/skills/systems-thinking/SKILL.md`](../../../.claude/skills/systems-thinking/SKILL.md)
  only points back to this file.
- Second step of the composition order in
  [docs/agents/agent-interoperability.md](../../../docs/agents/agent-interoperability.md):
  it consumes the `first-principles` decision record and hands its causal map
  to `red-team`.
- Parent: [../AGENTS.md](../AGENTS.md)

## Development Guidelines

- Use when a local change may alter behavior elsewhere in the system.
- This is the canonical copy; runtime wrappers such as
  `.claude/skills/systems-thinking/` stay pointers — change the workflow here.
- Keep `name` equal to the folder name; a rename must also update the wrapper,
  `.agent/SKILL_INDEX.md`, and the interoperability doc.
- Keep the output contract concrete (a causal map or table plus measurements)
  so reviewers can check it rather than accept narrative.
