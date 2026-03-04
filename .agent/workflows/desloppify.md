---
description: Codebase health scanner and technical debt tracker. Use when asked about code quality, dead code, technical debt, large files, god classes, or to create a cleanup plan.
---

# Desloppify

Crossover workflow from the `desloppify` Claude Code skill. This workflow maximizes the codebase "strict score" by detecting and fixing code quality issues, dead code, and duplication.

Read the full skill:
`view_file /Users/mini/Documents/GitHub/codomyrmex/.claude/skills/desloppify/SKILL.md`

## 1. Outer Loop: Scan & Check

```bash
desloppify scan --path .       # analyze the codebase
desloppify status              # check scores — are we at target?
```

Rescan periodically to measure progress, especially after batch fixes.

## 2. Inner Loop: Fix Issues

Repeat until the queue is clear:

```bash
desloppify next
```

1. `desloppify next` tells you literally what to fix next.
2. Fix the issue in the code.
3. Resolve it using the exact command provided by `next`.

If `next` suggests an auto-fixer, run `desloppify fix <fixer> --dry-run` to preview, then apply.

## 3. Planning & Clustering

Use `plan` to shape what `next` gives you:

```bash
desloppify plan                        # see the full ordered queue
desloppify plan cluster create <name>  # group related issues
desloppify plan focus <cluster>        # scope next to one cluster
desloppify plan defer <pat>            # push low-value items aside
```

## 4. Subjective Reviews

The scan will prompt you when a subjective review (design quality) is needed.

**Preferred One-Command Review:**

```bash
desloppify review --run-batches --runner codex --parallel --scan-after-import
```

Alternatively, you can split dimensions across N subagents and merge outputs, then run `desloppify review --import findings.json`. Follow the CLI instructions strictly.
