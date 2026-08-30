# AGENTS.md — `codomyrmex/.cursor/skills`

## Purpose
Cursor-runtime skill adapters. Each child folder carries a `SKILL.md` making a
skill invocable from Cursor agents.

## Layout
- `codomyrmex/` — full-spectrum workspace skill: PAI MCP bridge, ~600 production `@mcp_tool` lines, trust/verify workflows.
- `desloppify/` — desloppify CLI quality loop (mirror of the portable pattern).
- `fractals/` — recursive task decomposition with per-leaf git worktrees via `orchestrate_fractal_task`.

## Gotchas
- The portable canonical set lives in `.agents/skills/`; keep `name`/`description`
  frontmatter consistent across mirrors.
