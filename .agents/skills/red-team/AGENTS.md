# AGENTS.md — `codomyrmex/.agents/skills/red-team`

## Purpose

Portable repository-scoped skill: Adversarially test a design, implementation,
agent workflow, or tool surface for realistic failure and abuse paths within
authorized scope. Defined entirely by [`SKILL.md`](SKILL.md).

## Key Files

- [`SKILL.md`](SKILL.md) — canonical definition: frontmatter
  (`name: red-team`, `description`), a five-step workflow (assets, trust
  boundaries, and out-of-scope actions → enumerate abuse and failure paths →
  exercise the highest-risk paths with real components → record evidence and
  severity → re-test mitigations), and the reporting rule (findings first,
  ordered by risk).
- [`README.md`](README.md) — human signpost.

## Dependencies

- Claude Code wrapper: [`.claude/skills/red-team/SKILL.md`](../../../.claude/skills/red-team/SKILL.md)
  only points back to this file.
- Third step of the composition order in
  [docs/agents/agent-interoperability.md](../../../docs/agents/agent-interoperability.md),
  after `systems-thinking` and before `mcp-tool-use`.
- Its "real components over mocks" step matches the repository zero-mock policy
  in [../../../AGENTS.md](../../../AGENTS.md).
- Parent: [../AGENTS.md](../AGENTS.md)

## Development Guidelines

- Use for security, reliability, permission, and prompt-injection review.
- This is the canonical copy; runtime wrappers such as
  `.claude/skills/red-team/` stay pointers — change the workflow here.
- Never weaken the authorized-scope boundary or the ban on destructive actions;
  those lines are the skill's safety contract.
- Keep the distinction between confirmed findings and hypotheses, including the
  "not exploitable under current scope" outcome.
