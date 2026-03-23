---
description: Codebase health scanner and technical debt tracker. Use when asked about code quality, dead code, technical debt, large files, god classes, or to create a cleanup plan.
---

# Desloppify

Maximize the codebase **strict score** via the `desloppify` CLI. Full workflow, install steps, exclude policy, and execution rules: [`.agent/skills/desloppify/SKILL.md`](../skills/desloppify/SKILL.md).

## Quick reference

**Scan**

```bash
desloppify scan --path .
desloppify status
```

**Inner loop** (repeat until queue is clear)

```bash
desloppify next
```

Fix the issue, then run the **exact** `resolve` command from `next` output. Do not skip the resolve step.

**Planning**

```bash
desloppify plan
desloppify plan queue
desloppify plan cluster create <name>
desloppify plan focus <cluster>
desloppify plan defer <pat>
```

**Backlog** (inspection only; `next` drives work)

```bash
desloppify backlog
```

**Subjective review** (when prompted)

```bash
desloppify review --run-batches --runner codex --parallel --scan-after-import
```

Or follow `desloppify review --import` per CLI instructions. If `next` suggests an auto-fixer: `desloppify fix <fixer> --dry-run` then apply.

Rescan periodically after batch fixes. Follow scan/agent instructions from the tool, not improvised analysis.
