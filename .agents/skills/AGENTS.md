# AGENTS.md — `codomyrmex/.agents/skills`

## Purpose

The canonical, repository-scoped portable skill library. Runtime wrappers (for
example `.claude/skills/<name>/SKILL.md`) point back to these definitions
instead of copying them.

## Key Files

One folder per skill, each with a single `SKILL.md` plus a `README.md`/`AGENTS.md` pair:

- [`agent-interop/`](agent-interop/SKILL.md) — keep Codex, Claude Code, and
  Hermes aligned through portable skills and shared MCP contracts.
- [`first-principles/`](first-principles/SKILL.md) — reduce an ambiguous problem
  to verified facts, constraints, and explicit decisions.
- [`mcp-tool-use/`](mcp-tool-use/SKILL.md) — schema inspection,
  least-privilege selection, approvals, and verified results for MCP calls.
- [`red-team/`](red-team/SKILL.md) — adversarial review of realistic failure
  and abuse paths within authorized scope.
- [`systems-thinking/`](systems-thinking/SKILL.md) — map boundaries,
  dependencies, feedback loops, and leverage points.
- [`README.md`](README.md) — human signpost.

## Dependencies

- Discovery: Codex reads this directory directly; Claude Code uses the wrappers
  in `.claude/skills/`; Hermes lists it under `skills.external_dirs`
  ([example](../../config/hermes_external_skills.example.yaml)).
- Composition order for a substantial change
  (`first-principles -> systems-thinking -> red-team -> mcp-tool-use -> agent-interop`)
  is defined in [docs/agents/agent-interoperability.md](../../docs/agents/agent-interoperability.md).
- Indexed in [`.agent/SKILL_INDEX.md`](../../.agent/SKILL_INDEX.md).
- Parent: [../AGENTS.md](../AGENTS.md)

## Development Guidelines

- Keep skill frontmatter (`name`, `description`) stable — runtimes index by it;
  `name` must match the folder name.
- New skills must be added to the crossover index (`.agent/SKILL_INDEX.md`), the
  skill table in the interoperability doc, and a `.claude/skills/<name>/`
  pointer wrapper.
- Follow the portable Agent Skills layout: concise frontmatter, one `SKILL.md`,
  supporting files only when a skill needs them.
