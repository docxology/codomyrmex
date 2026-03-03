# Documents / Transformation Test Specification

**Version**: v1.0.8 | **Status**: Active | **Last Updated**: March 2026

## Overview

Specification for the `documents/unit/transformation` test suite.

## Zero-Mock Policy

- No `unittest.mock`, `MagicMock`, or `pytest-mock`
- External dependencies guarded with `@pytest.mark.skipif`
- All tests use real implementations

## Test Structure

```
tests/unit/documents/unit/transformation/
    __init__.py
    test_transformation.py
```

## Functional Requirements

1. All public API methods in `documents` must have at least one test
2. Edge cases and error conditions must be explicitly tested
3. Tests must be deterministic (no random state without fixed seeds)

## Dependencies

**Requires**: `pytest`, `uv sync --extra documents` (if module has optional deps)

## Navigation

- [README.md](README.md) | [AGENTS.md](AGENTS.md) | [Source](../../../../../../documents/)
