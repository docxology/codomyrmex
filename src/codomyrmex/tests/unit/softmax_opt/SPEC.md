# Softmax Optimization Test Specification

**Version**: v1.1.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

Specification for the `softmax_opt` test suite.

## Zero-Mock Policy

- No `unittest.mock`, `MagicMock`, or `pytest-mock`
- External dependencies guarded with `@pytest.mark.skipif`
- All tests use real implementations

## Test Structure

```
tests/unit/softmax_opt/
    __init__.py
    test_softmax_opt.py
```

## Functional Requirements

1. All public API methods in `softmax_opt` must have at least one test
2. Edge cases and error conditions must be explicitly tested
3. Tests must be deterministic (no random state without fixed seeds)

## Dependencies

**Requires**: `pytest`, `uv sync --extra softmax_opt` (if module has optional deps)

## Navigation

- [README.md](README.md) | [AGENTS.md](AGENTS.md) | [Source](../../../../softmax_opt/)
