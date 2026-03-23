---
name: desloppify
description: >-
  Improves codebase quality via the desloppify CLI — install, exclude noise, scan, and drive
  the next/resolve execution loop to raise strict score. Use when the user invokes /desloppify,
  asks for tech-debt cleanup, desloppify, strict score, or codebase health scanning.
---

# Desloppify

Goal: raise the **strict** score. The scoring resists gaming; improvements require real code quality work.

## 1. Install (Python 3.11+)

Upstream install:

```bash
pip install --upgrade "desloppify[full]"
```

**Codomyrmex:** prefer `uv` — after `uv sync`, in the project environment:

```bash
uv pip install "desloppify[full]"
```

For a global CLI, use `uv tool install` with the same extra if you want desloppify available outside the project venv.

## 2. Workflow guide for your IDE

Install the bundled workflow instructions for the user’s stack:

```bash
desloppify update-skill claude    # or: cursor, codex, copilot, droid, windsurf, gemini
```

Default to **`cursor`** when the session is Cursor; otherwise match the user’s stated tool.

## 3. Local state and git

Keep **`.desloppify/`** out of version control (local scan state). This repo already ignores `.desloppify/` in `.gitignore`; do not commit that directory.

## 4. Excludes before scan

Before the first meaningful scan, identify paths that should not be analyzed (vendor trees, build output, generated code, git worktrees, huge submodules, caches).

- Run `desloppify exclude <path>` for **obvious** noise.
- **Pause and ask the human** before excluding anything ambiguous.

**Codomyrmex-oriented examples** (exclude when appropriate, not blindly): `node_modules/`, `htmlcov/`, `.gitnexus/`, `__pycache__/`, `.venv/`, `venv/`, submodule checkouts, `src/codomyrmex/agents/hermes/evolution/` (special dependency layout per `CLAUDE.md`), vendored or generated trees already listed in `.gitignore`.

## 5. Scan

```bash
desloppify scan --path .
```

Use `.` for the whole repo, or a subtree (e.g. `src/`). Rescan periodically after batch fixes.

## 6. Main loop — `next` is the queue

**`desloppify next`** is the living execution queue, not the full backlog. It names what to fix now, which file, and the **`resolve` command** to run when done.

Repeat until clear:

1. Run `desloppify next`.
2. Implement the fix properly (large refactors and small fixes deserve the same care).
3. Run the **exact** resolve command from the output.
4. Go to step 1.

Follow **agent instructions emitted by the scan / CLI**; do not replace them with ad-hoc analysis.

If `next` points at an auto-fixer: `desloppify fix <fixer> --dry-run` first, then apply.

## 7. Backlog vs plan

- **`desloppify backlog`** — inspect broader open work; not the primary driver.
- **`desloppify plan`** / **`desloppify plan queue`** — reorder priorities, cluster related issues. Use when you need to shape what `next` surfaces.

## 8. Subjective / batch reviews

When the tool prompts for subjective or design review, follow its CLI guidance. Example pattern (adjust runner to what the user has):

```bash
desloppify review --run-batches --runner codex --parallel --scan-after-import
```

Alternatively split work across agents, merge outputs, then `desloppify review --import findings.json` per CLI docs.

## 9. Repo expectations (Codomyrmex)

- Tests: **zero-mock** policy — use `uv run pytest` after substantive change batches.
- Prefer **`uv`** for Python commands consistently with project docs.

## 10. Optional quick reference

| Action | Command |
|--------|---------|
| Scores | `desloppify status` |
| Plan view | `desloppify plan` |
| Cluster | `desloppify plan cluster create <name>` |
| Focus cluster | `desloppify plan focus <cluster>` |
| Defer pattern | `desloppify plan defer <pat>` |
