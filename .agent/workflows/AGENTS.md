# AGENTS.md — `codomyrmex/.agent/workflows`

## Purpose

Workflow definitions consumed by Claude Code / Antigravity runtimes from the
`.agent` surface. Each `*.md` file is one slash command (`/<file stem>`) with a
YAML frontmatter `description` and numbered steps.

## Key Files

- Codomyrmex tool bridges (MCP/PAI calls run through `uv run python -c`):
  `codomyrmexAnalyze.md` (analyze a path), `codomyrmexDocs.md` (fetch a module's
  README or SPEC), `codomyrmexMemory.md` (store agentic memory),
  `codomyrmexSearch.md` (regex code search), `codomyrmexStatus.md` (system and
  PAI health), `codomyrmexVerify.md` (read-only capability audit),
  `codomyrmexTrust.md` (promote tools to TRUSTED, enabling destructive operations).
- [`codomyrmexWorktree.md`](codomyrmexWorktree.md) — git worktree coordination
  for concurrent agents (linked from the root `CLAUDE.md`).
- Quality and testing: `coveragePush.md`, `moduleHealthAudit.md` (RASP, MCP,
  PAI.md, coverage), `tdd.md`, `propertyBasedTesting.md`,
  `systematicDebugging.md`, `modernPython.md`, `securityAudit.md` — the last
  five bridge Superpowers and Trail of Bits plugin skills via `view_file`.
- `desloppify.md` (points to [`../skills/desloppify/SKILL.md`](../skills/desloppify/SKILL.md))
  and `gitnexus.md` (GitNexus CLI).
- [`README.md`](README.md) — human signpost listing every workflow.

## Dependencies

- `tool_list_workflows()` in
  [`src/codomyrmex/agents/pai/mcp/proxy_tools.py`](../../src/codomyrmex/agents/pai/mcp/proxy_tools.py)
  lists every `*.md` here with its frontmatter `description`.
- `check_workflows()` in [`src/codomyrmex/cli/doctor.py`](../../src/codomyrmex/cli/doctor.py)
  (`codomyrmex doctor`) counts files whose frontmatter lacks `description:` as invalid.
- Tests: `tests/unit/agents/pai/test_mcp_proxy_tools.py` and
  `tests/unit/agents/pai/test_pai_bridge_hardening.py`.
- Described in [docs/modules/agents/PAI/WORKFLOWS.md](../../docs/modules/agents/PAI/WORKFLOWS.md)
  and [docs/development/multi-agent-git.md](../../docs/development/multi-agent-git.md).
- Parent: [../AGENTS.md](../AGENTS.md) · Skill index: [../SKILL_INDEX.md](../SKILL_INDEX.md)

## Development Guidelines

- Workflows reference skills by name; keep names aligned with `../SKILL_INDEX.md`.
- Workflows encode codomyrmex trust/verify patterns (codomyrmexTrust, codomyrmexVerify) —
  do not weaken their verification steps when editing.
- Start every workflow with `---` frontmatter containing `description:`, and
  quote the value when it contains a colon followed by a space, or YAML
  parsing fails and the workflow is listed with "No description".
- `codomyrmex doctor` and `tool_list_workflows()` skip the directory's own
  documentation (`AGENTS.md`, `README.md`, `SPEC.md`, `PAI.md`); any other
  Markdown file here is treated as a workflow.
- `// turbo` lines mark the following step for auto-run in Antigravity; only
  place one before a trust-escalating or destructive step when invoking the
  workflow is itself the user's explicit consent (as with `/codomyrmexTrust`).
- Use repository-relative commands (`cd "$(git rev-parse --show-toplevel)"`),
  never a machine-specific absolute checkout path.
- Quote numeric gates from `pyproject.toml` (`fail_under = 60`), not from
  memory.
