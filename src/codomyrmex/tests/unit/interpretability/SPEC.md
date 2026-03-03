# Interpretability Test Specification

**Version**: v1.0.8 | **Status**: Active | **Last Updated**: March 2026

## Overview

Specification for the `interpretability` test suite.

## Zero-Mock Policy

- No `unittest.mock`, `MagicMock`, or `pytest-mock`
- External dependencies guarded with `@pytest.mark.skipif`
- All tests use real implementations

## Test Structure

```
tests/unit/interpretability/
    __init__.py
    test_interpretability.py
```

## Functional Requirements

1. All public API methods in `interpretability` must have at least one test
2. Edge cases and error conditions must be explicitly tested
3. Tests must be deterministic (no random state without fixed seeds)

## Dependencies

**Requires**: `pytest`, `uv sync --extra interpretability` (if module has optional deps)

## Navigation

- [README.md](README.md) | [AGENTS.md](AGENTS.md) | [Source](../../../../interpretability/)
