# Model Merger Test Specification

**Version**: v1.0.8 | **Status**: Active | **Last Updated**: March 2026

## Overview

Specification for the `model_merger` test suite.

## Zero-Mock Policy

- No `unittest.mock`, `MagicMock`, or `pytest-mock`
- External dependencies guarded with `@pytest.mark.skipif`
- All tests use real implementations

## Test Structure

```
tests/unit/model_merger/
    __init__.py
    test_model_merger.py
```

## Functional Requirements

1. All public API methods in `model_merger` must have at least one test
2. Edge cases and error conditions must be explicitly tested
3. Tests must be deterministic (no random state without fixed seeds)

## Dependencies

**Requires**: `pytest`, `uv sync --extra model_merger` (if module has optional deps)

## Navigation

- [README.md](README.md) | [AGENTS.md](AGENTS.md) | [Source](../../../../model_merger/)
