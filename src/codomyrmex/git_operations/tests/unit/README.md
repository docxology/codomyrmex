# unit

## Signposting
- **Parent**: [Parent](../README.md)
- **Children**:
    - None
- **Key Artifacts**:
    - [Agent Guide](AGENTS.md)
    - [Functional Spec](SPEC.md)

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Overview

Test files and validation suites for unit.

## Directory Contents
- `README.md` – File
- `SPEC.md` – File

## Navigation
- **Technical Documentation**: [AGENTS.md](AGENTS.md)
- **Functional Specification**: [SPEC.md](SPEC.md)
- **Parent Directory**: [tests](../README.md)
- **Project Root**: [README](../../../../../README.md)

## Getting Started

This directory contains unit tests for the git_operations module.

### Running Unit Tests

```bash
pytest src/codomyrmex/git_operations/tests/unit/
```

### Example Unit Test

```python
import pytest
from codomyrmex.git_operations import check_git_availability, is_git_repository

def test_check_git_availability():
    """Test that Git availability check works."""
    result = check_git_availability()
    assert isinstance(result, bool)

def test_is_git_repository(tmp_path):
    """Test repository detection."""
    # Test with non-repository path
    assert is_git_repository(str(tmp_path)) == False
```

