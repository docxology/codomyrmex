# integration

## Signposting
- **Parent**: [Parent](../README.md)
- **Children**:
    - None
- **Key Artifacts**:
    - [Agent Guide](AGENTS.md)
    - [Functional Spec](SPEC.md)

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Overview

Test files and validation suites for integration.

## Directory Contents
- `README.md` – File
- `SPEC.md` – File

## Navigation
- **Technical Documentation**: [AGENTS.md](AGENTS.md)
- **Functional Specification**: [SPEC.md](SPEC.md)
- **Parent Directory**: [tests](../README.md)
- **Project Root**: [README](../../../../../README.md)

## Getting Started

This directory contains integration tests for the git_operations module.

### Running Integration Tests

```bash
pytest src/codomyrmex/git_operations/tests/integration/
```

### Example Integration Test

```python
import pytest
from codomyrmex.git_operations import (
    initialize_git_repository,
    create_branch,
    add_files,
    commit_changes,
    get_current_branch
)

def test_complete_workflow(tmp_path):
    """Test a complete Git workflow."""
    repo_path = str(tmp_path / "test_repo")
    
    # Initialize repository
    assert initialize_git_repository(repo_path) == True
    
    # Create branch
    assert create_branch("feature/test", repo_path) == True
    
    # Verify branch
    assert get_current_branch(repo_path) == "feature/test"
```

