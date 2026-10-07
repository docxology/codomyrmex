# AGENTS.md — `codomyrmex/.agent`

## Purpose

Runtime-local agent configuration for the Claude Code / Antigravity crossover:
a skill index, runtime-scoped skills, and slash-command workflow definitions.

## Key Files

- [`SKILL_INDEX.md`](SKILL_INDEX.md) — index of Claude Code plugins and their
  `SKILL.md` paths (Antigravity reads any skill on demand via `view_file`), the
  repository-scoped portable skills, and the auto-loaded workflow bridges.
- [`skills/`](skills/README.md) — runtime-scoped skills; currently `desloppify`,
  whose canonical definition lives here.
- [`workflows/`](workflows/README.md) — 17 slash-command workflows, each a
  Markdown file with a YAML `description` frontmatter field.
- [`README.md`](README.md) — human signpost.

## Dependencies

- `workflows/` is read by code: `tool_list_workflows()` in
  [`src/codomyrmex/agents/pai/mcp/proxy_tools.py`](../src/codomyrmex/agents/pai/mcp/proxy_tools.py)
  lists it for the PAI bridge, and `check_workflows()` in
  [`src/codomyrmex/cli/doctor.py`](../src/codomyrmex/cli/doctor.py) reports an
  error from `codomyrmex doctor` when it is missing.
- `skills/` is the default search and scaffold path of
  [`scripts/skills/skill_utils.py`](../scripts/skills/skill_utils.py)
  (`list`, `show`, `create`).
- Portable, runtime-neutral skills live in [`.agents/skills/`](../.agents/skills/README.md);
  Cursor reaches `desloppify` through the stub at
  [`.cursor/skills/desloppify/SKILL.md`](../.cursor/skills/desloppify/SKILL.md).
- Parent: [../README.md](../README.md) · Root contract: [../AGENTS.md](../AGENTS.md)

## Development Guidelines

- Runtime-scoped skills here serve this runtime; the portable
  repository-scoped set lives in `.agents/skills/`. Keep `SKILL_INDEX.md` in
  sync when either set changes.
- Do not move or rename `workflows/` without updating `proxy_tools.py`,
  `doctor.py`, and their tests under `tests/unit/agents/pai/`.
- `SKILL_INDEX.md` records version-pinned plugin cache paths under
  `~/.claude/plugins/cache/`; refresh them when a plugin version changes.
- The comprehensive link gate (`scripts/documentation/validate_links_comprehensive.py`)
  skips `.agent/`, so verify relative links in this tree by hand.
