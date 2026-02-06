# Git Operations Documentation

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

Git repository management and operations.

## Key Features

- **Clone** — Clone repositories
- **Commits** — Commit operations
- **Branches** — Branch management
- **Diff** — Diff generation

## Quick Start

```python
from codomyrmex.git_operations import GitRepo

repo = GitRepo("./my_project")
status = repo.status()
repo.add(["src/main.py"])
repo.commit("Add feature")
repo.push()
```

## Directory Contents

| File | Description |
|------|-------------|
| `README.md` | This file |
| `SPEC.md` | Technical specification |

## Navigation

- **Source**: [src/codomyrmex/git_operations/](../../../src/codomyrmex/git_operations/)
- **Parent**: [Modules](../README.md)
