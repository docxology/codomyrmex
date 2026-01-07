# tests

## Signposting
- **Parent**: [git_operations](../README.md)
- **Children**:
    - [integration](integration/README.md)
    - [unit](unit/README.md)
- **Key Artifacts**:
    - [Agent Guide](AGENTS.md)
    - [Functional Spec](SPEC.md)

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Overview

Test files and validation suites.

## Directory Contents
- `README.md` – File
- `SPEC.md` – File
- `integration/` – Subdirectory
- `unit/` – Subdirectory

## Navigation
- **Technical Documentation**: [AGENTS.md](AGENTS.md)
- **Functional Specification**: [SPEC.md](SPEC.md)
- **Parent Directory**: [git_operations](../README.md)
- **Project Root**: [README](../../../../README.md)

## Getting Started

This directory contains test suites for the git_operations module.

### Running Tests

```bash
# Run all tests
pytest src/codomyrmex/git_operations/tests/

# Run only unit tests
pytest src/codomyrmex/git_operations/tests/unit/

# Run only integration tests
pytest src/codomyrmex/git_operations/tests/integration/
```

### Test Structure

- `unit/` - Unit tests for individual functions
- `integration/` - Integration tests for complete workflows

### Example Test

```python
from codomyrmex.git_operations import check_git_availability

def test_git_availability():
    assert check_git_availability() == True
```

