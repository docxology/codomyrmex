# Semantic Router Test Specification

**Version**: v1.1.9 | **Status**: Active | **Last Updated**: March 2026

## Overview

Specification for the `semantic_router` test suite.

## Zero-Mock Policy

- No `unittest.mock`, `MagicMock`, or `pytest-mock`
- External dependencies guarded with `@pytest.mark.skipif`
- All tests use real implementations

## Test Structure

```
tests/unit/semantic_router/
    __init__.py
    test_semantic_router.py
```

## Functional Requirements

1. All public API methods in `semantic_router` must have at least one test
2. Edge cases and error conditions must be explicitly tested
3. Tests must be deterministic (no random state without fixed seeds)

## Dependencies

**Requires**: `pytest`, `uv sync --extra semantic_router` (if module has optional deps)

## Navigation

- [README.md](README.md) | [AGENTS.md](AGENTS.md) | [Source](../../../semantic_router/)
