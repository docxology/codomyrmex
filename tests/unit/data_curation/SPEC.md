# Data Curation Test Specification

**Version**: v1.1.9 | **Status**: Active | **Last Updated**: March 2026

## Overview

Specification for the `data_curation` test suite.

## Zero-Mock Policy

- No `unittest.mock`, `MagicMock`, or `pytest-mock`
- External dependencies guarded with `@pytest.mark.skipif`
- All tests use real implementations

## Test Structure

```
tests/unit/data_curation/
    __init__.py
    test_data_curation.py
```

## Functional Requirements

1. All public API methods in `data_curation` must have at least one test
2. Edge cases and error conditions must be explicitly tested
3. Tests must be deterministic (no random state without fixed seeds)

## Dependencies

**Requires**: `pytest`, `uv sync --extra data_curation` (if module has optional deps)

## Navigation

- [README.md](README.md) | [AGENTS.md](AGENTS.md) | [Source](../../../data_curation/)
