# Text-to-SQL Test Specification

**Version**: v1.1.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

Specification for the `text_to_sql` test suite.

## Zero-Mock Policy

- No `unittest.mock`, `MagicMock`, or `pytest-mock`
- External dependencies guarded with `@pytest.mark.skipif`
- All tests use real implementations

## Test Structure

```
tests/unit/text_to_sql/
    __init__.py
    test_text_to_sql.py
```

## Functional Requirements

1. All public API methods in `text_to_sql` must have at least one test
2. Edge cases and error conditions must be explicitly tested
3. Tests must be deterministic (no random state without fixed seeds)

## Dependencies

**Requires**: `pytest`, `uv sync --extra text_to_sql` (if module has optional deps)

## Navigation

- [README.md](README.md) | [AGENTS.md](AGENTS.md) | [Source](../../../../text_to_sql/)
