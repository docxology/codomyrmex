---
description: Manage git worktrees for safe multi-agent concurrent development
---

# Multi-Agent Git Worktree Coordination

This workflow documents how to safely run multiple Claude Code instances (or other AI
agents) concurrently on the same repository using git worktrees, avoiding index.lock
conflicts and merge collisions.

## Background

Claude Code creates agent worktrees at `.claude/worktrees/agent-<id>/`. Each worktree
is a full working copy sharing the same `.git` directory. This means:

- ✅ Each worktree has its own working tree and index
- ✅ Changes in one worktree don't affect others until merged
- ⚠️ Git operations that touch `.git/index.lock` can still conflict
- ⚠️ All worktrees share the same remote, so push/pull affects all

## Current Setup

```bash
# List all active worktrees
git worktree list

# Typical output:
# /Users/mini/Documents/GitHub/codomyrmex                           041ea3f9 [main]
# .claude/worktrees/agent-a04c4e4b   dea00ccd [worktree-agent-a04c4e4b]
# .claude/worktrees/agent-a4372589   dea00ccd [worktree-agent-a4372589]
# ...
```

## Safe Operations (No Lock Required)

These operations are safe to run in any worktree without coordination:

```bash
# Reading operations — always safe
git status
git log
git diff
git show
git branch --list

# Worktree-local operations — each has its own index
git add <file>           # in the worktree's own directory
git checkout <file>      # in the worktree's own directory
```

## Dangerous Operations (Lock Required)

These operations touch `.git/index.lock` and will conflict if another agent is running them:

```bash
# These acquire the index lock:
git add -A               # from main worktree
git commit               # from main worktree
git merge
git rebase
git stash
git pull
git push
```

## Coordination Protocol

### Before Git Write Operations

// turbo-all

1. Check if any git process is holding the lock:

```bash
ls -la .git/index.lock 2>/dev/null && echo "LOCKED" || echo "FREE"
```

1. If locked, wait and retry (do NOT blindly remove the lock):

```bash
# Wait for lock to clear (max 30 seconds)
for i in $(seq 1 30); do
  [ ! -f .git/index.lock ] && break
  sleep 1
done
```

1. If the lock persists > 60 seconds, it's likely stale — safe to remove:

```bash
rm -f .git/index.lock
```

1. Perform git operations immediately after clearing/confirming no lock.

### Creating a New Worktree

```bash
# Create a worktree for a specific task
AGENT_ID=$(openssl rand -hex 4)
git worktree add .claude/worktrees/agent-$AGENT_ID -b worktree-agent-$AGENT_ID

# Work in the worktree (avoids main index conflicts entirely)
cd .claude/worktrees/agent-$AGENT_ID
# ... make changes ...
git add -A && git commit -m "agent work"

# Merge back to main
cd /path/to/main/repo
git merge worktree-agent-$AGENT_ID
```

### Cleaning Up Worktrees

```bash
# List stale worktrees
git worktree list

# Remove a worktree (branch remains)
git worktree remove .claude/worktrees/agent-<id>

# Prune all stale worktree tracking info
git worktree prune

# Remove the worktree branch
git branch -D worktree-agent-<id>

# Clean up ALL stale worktrees at once
git worktree prune && git worktree list
for branch in $(git branch --list 'worktree-agent-*'); do
  git branch -D $branch 2>/dev/null
done
```

## Best Practices

1. **Worktree per agent session**: Each Claude Code session should use its own worktree
2. **Never commit from main while agents run**: Use worktrees for all agent writes
3. **Use `--no-verify`** for agent commits to avoid pre-commit hook contention
4. **Atomic stage+commit**: Always `git add -A && git commit` in one command to minimize lock time
5. **Add large generated files to `.gitignore`** before committing (avoid 100MB GitHub limit)
6. **Clean stale worktrees regularly**: Run `git worktree prune` periodically

## Troubleshooting

### index.lock Persists After Agent Crash

```bash
# Verify no git process is running
ps aux | grep 'git' | grep -v grep

# If no process found, safely remove
rm -f .git/index.lock
```

### Push Rejected (Large Files)

```bash
# Find files over 50MB
find . -name '*.json' -size +50M -not -path './.git/*'

# Add to .gitignore and remove from staging
echo "path/to/large_file.json" >> .gitignore
git rm --cached path/to/large_file.json
git commit --amend --no-edit --no-verify
```

### Worktree Branch Conflicts

```bash
# If worktree branch diverged too far, rebase onto main
cd .claude/worktrees/agent-<id>
git rebase main
```
