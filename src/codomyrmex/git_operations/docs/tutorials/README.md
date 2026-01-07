# tutorials

## Signposting
- **Parent**: [docs](../README.md)
- **Children**:
    - None
- **Key Artifacts**:
    - [Agent Guide](AGENTS.md)
    - [Functional Spec](SPEC.md)

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Overview

Documentation files and guides for tutorials.

## Directory Contents
- `README.md` – File
- `SPEC.md` – File
- `creating_feature_branch_tutorial.md` – File

## Navigation
- **Technical Documentation**: [AGENTS.md](AGENTS.md)
- **Functional Specification**: [SPEC.md](SPEC.md)
- **Parent Directory**: [docs](../README.md)
- **Project Root**: [README](../../../../../README.md)

## Getting Started

This directory contains tutorials for using the git_operations module.

### Available Tutorials

- [Creating Feature Branch](creating_feature_branch_tutorial.md) - Step-by-step guide for feature branch workflows

### Example Usage

```python
from codomyrmex.git_operations import (
    initialize_git_repository,
    create_branch,
    add_files,
    commit_changes
)

# Initialize repository
initialize_git_repository("/path/to/repo")

# Create feature branch
create_branch("feature/new-feature", "/path/to/repo")

# Add and commit files
add_files(["new_file.py"], "/path/to/repo")
commit_changes("Add new feature", "/path/to/repo")
```

