# Agents / CLI Handlers Test Specification

**Version**: v1.0.8 | **Status**: Active | **Last Updated**: March 2026

## Overview

Specification for the `agents/cli` test suite.

## Zero-Mock Policy

- No `unittest.mock`, `MagicMock`, or `pytest-mock`
- External dependencies guarded with `@pytest.mark.skipif`
- All tests use real implementations

## Test Structure

```
tests/unit/agents/cli/
    __init__.py
    test_handlers.py
```

## Functional Requirements

1. All public API methods in `agents/cli` must have at least one test
2. Edge cases and error conditions must be explicitly tested
3. Tests must be deterministic (no random state without fixed seeds)

## Dependencies

**Requires**: `pytest`, `uv sync --extra agents` (if module has optional deps)

## Navigation

- [README.md](README.md) | [AGENTS.md](AGENTS.md) | [Source](../../../../../agents/cli/)
