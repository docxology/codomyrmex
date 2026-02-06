# Agent Guidelines - Git Operations

## Module Overview

Git repository operations: commits, branches, merges, and history.

## Key Classes

- **GitRepo** — Repository operations
- **Commit** — Commit representation
- **Branch** — Branch management
- **DiffManager** — View diffs

## Agent Instructions

1. **Check status first** — Verify clean state
2. **Branch often** — Feature branches for work
3. **Small commits** — Atomic, focused commits
4. **Meaningful messages** — Descriptive commit messages
5. **Pull before push** — Avoid merge conflicts

## Common Patterns

```python
from codomyrmex.git_operations import GitRepo, Branch

# Open repository
repo = GitRepo(".")

# Check status
status = repo.status()
if status.is_dirty:
    print(f"Modified: {status.modified_files}")

# Commit changes
repo.add(["src/main.py"])
repo.commit("feat: add new feature")

# Branch operations
branch = Branch(repo)
branch.create("feature/new-thing")
branch.checkout("feature/new-thing")

# View history
for commit in repo.log(limit=10):
    print(f"{commit.hash[:7]} - {commit.message}")
```

## Testing Patterns

```python
# Verify status
repo = GitRepo(".")
status = repo.status()
assert hasattr(status, "is_dirty")

# Verify log
commits = repo.log(limit=5)
assert len(commits) <= 5

# Verify branch listing
branches = repo.branches()
assert "main" in branches or "master" in branches
```

## Navigation

- [README](README.md) | [SPEC](SPEC.md) | [PAI](PAI.md)
