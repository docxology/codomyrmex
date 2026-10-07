# AGENTS.md — `codomyrmex/.agent/skills/desloppify`

## Purpose

Canonical definition of the desloppify skill: drives the desloppify CLI to raise
the codebase strict score — install, exclude noise, scan, then the
next/resolve loop. Other runtimes reach it through pointer stubs.

## Key Files

- [`SKILL.md`](SKILL.md) — the skill definition (trigger: /desloppify, tech-debt
  cleanup, strict score, codebase health scanning), in ten sections: install
  with `uv`, IDE workflow guide, local state, excludes, scan, the `next` →
  fix → `resolve` loop, backlog vs plan, subjective reviews, Codomyrmex
  expectations, and a command quick reference.
- [`README.md`](README.md) — human signpost.

## Dependencies

- Pointer stubs that defer to this file:
  [`.cursor/skills/desloppify/SKILL.md`](../../../.cursor/skills/desloppify/SKILL.md)
  (Cursor discovery) and the `/desloppify` workflow
  [`../../workflows/desloppify.md`](../../workflows/desloppify.md).
- Tooling: `desloppify[full]>=0.9.14` is in the `dev` dependency group of
  [`pyproject.toml`](../../../pyproject.toml), so `uv sync` installs the CLI;
  scan state goes to `.desloppify/`, which `.gitignore` excludes.
- Parent: [../AGENTS.md](../AGENTS.md)

## Development Guidelines

- This is the source of truth: edit `SKILL.md` here and keep the Cursor stub and
  the workflow as pointers rather than copies.
- Keep the Codomyrmex-specific exclude list in `SKILL.md` aligned with
  `.gitignore` and `CLAUDE.md` (for example `src/codomyrmex/agents/hermes/evolution/`).
- Keep the instruction to run the exact `resolve` command from `desloppify next`
  output; the loop depends on it.
- Never commit `.desloppify/` scan state.
