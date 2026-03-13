# Multi-Agent Git Coordination

**Version**: v1.2.2 | **Status**: Active | **Last Updated**: March 2026

## Overview

When multiple Claude Code instances, CI runners, or AI agents operate concurrently on this repository, git `.git/index.lock` conflicts are the primary failure mode. This guide documents the coordination protocol established in `CLAUDE.md`.

## The Core Problem

Git uses `.git/index.lock` as a mutex for all staging operations. If two processes attempt `git add` simultaneously, the second fails:

```
fatal: Unable to create '.git/index.lock': File exists.
```

Pre-commit hooks on this repo run across 900+ files. A single commit can hold the lock for 20+ minutes, blocking all parallel agents.

## Rules

### Rule 1 — Use `--no-verify` for All Agent Commits
Pre-commit hooks take 20+ minutes on this repo. Always bypass for automated/agent commits:
```bash
git add -A && git commit --no-verify -m "message"
```

### Rule 2 — Atomic Stage + Commit
Always chain `git add` and `git commit` in one shell command to minimize lock hold time:
```bash
# CORRECT — acquires lock once, releases atomically
git add -A && git commit --no-verify -m "msg"

# WRONG — holds index state open between commands (race window)
git add -A
git commit -m "msg"
```

### Rule 3 — Check for Existing Lock Before Any Git Write
```bash
ls .git/index.lock 2>/dev/null && echo "LOCK EXISTS — wait or investigate" || echo "clear"
```

### Rule 4 — Clear Stale Locks Safely
Only remove the lock if no git process is actually running:
```bash
# Step 1: Check for running git processes
ps aux | grep git | grep -v grep
# Step 2: If none found and lock is >60s old — safe to remove
rm -f .git/index.lock
```

### Rule 5 — Use Worktrees for Parallel Work
Each git worktree gets its own `.git/worktrees/<name>/` with no shared lock:
```bash
# Create an isolated worktree for parallel agent work
git worktree add .worktrees/agent-feature -b agent-feature
cd .worktrees/agent-feature
# This agent can git add/commit freely — no lock contention
```
See `.agent/workflows/codomyrmexWorktree.md` for the managed creation workflow.

### Rule 6 — Check for Large Files Before Commit
GitHub rejects files over 100MB. Check before committing:
```bash
find . -not -path './.git/*' -size +50M
```

## Quick Reference

| Operation | Lock needed? | Safe in parallel? |
|-----------|-------------|-------------------|
| `git status` | No | Yes |
| `git log` | No | Yes |
| `git diff` | No | Yes |
| `git show` | No | Yes |
| `git add` | Yes | No |
| `git commit` | Yes | No |
| `git push` | No (index) | Usually yes |
| `git fetch` | No (index) | Yes |

## Worktree Cleanup

```bash
# Prune stale worktree metadata
git worktree prune

# Remove agent worktree branches after merging
git branch --list 'worktree-agent-*' | xargs git branch -D 2>/dev/null
```

## Navigation

- **Parent**: [Development](README.md)
- **Root**: [docs/](../README.md)
- **CLAUDE.md** (canonical rules): [../../CLAUDE.md](../../CLAUDE.md)
- **Worktree Workflow**: [../../.agent/workflows/codomyrmexWorktree.md](../../.agent/workflows/codomyrmexWorktree.md)
