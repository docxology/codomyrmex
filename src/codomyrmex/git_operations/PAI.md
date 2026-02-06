# Personal AI Infrastructure — Git Operations Module

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

The Git Operations module provides PAI integration for git repository management.

## PAI Capabilities

### Repository Operations

Manage git repos:

```python
from codomyrmex.git_operations import GitRepo

repo = GitRepo("./my_project")
status = repo.status()
repo.add(["src/main.py"])
repo.commit("Add feature")
```

### Branch Management

Work with branches:

```python
from codomyrmex.git_operations import GitRepo

repo = GitRepo(".")
repo.checkout("feature-branch", create=True)
repo.merge("main")
```

## PAI Integration Points

| Component | PAI Use Case |
|-----------|-------------|
| `GitRepo` | Repo operations |
| `commit` | Commit changes |
| `push/pull` | Remote sync |

## Navigation

- [README](README.md) | [AGENTS](AGENTS.md) | [SPEC](SPEC.md)
