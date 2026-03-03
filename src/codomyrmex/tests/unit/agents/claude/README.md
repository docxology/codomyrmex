# Agents / Claude Mixins Tests

**Version**: v1.0.8 | **Status**: Active | **Last Updated**: March 2026

## Overview

Unit tests for the `agents/claude` sub-module. Covers CodeIntelMixin (code review, diff generation, explanation) and ExecutionMixin (execute, stream, cost calculation).

## Test Coverage

| Test Class | What It Tests |
|-----------|---------------|
| `TestCodeIntelMixin` | Code review output parsing, unified diff generation, method presence |
| `TestExecutionMixin` | Execute/stream methods, Claude pricing dict, cost calculation |

## Test Structure

```
tests/unit/agents/claude/
    __init__.py
    test_claude_mixins.py
```

## Running Tests

```bash
# Run all tests for this module
uv run pytest src/codomyrmex/tests/unit/agents/claude/ -v

# Run with coverage
uv run pytest src/codomyrmex/tests/unit/agents/claude/ --cov=src/codomyrmex/agents/claude -v
```

## Test Policy

All tests follow the zero-mock policy: no `unittest.mock`, `MagicMock`, or `monkeypatch`.
External dependencies use `@pytest.mark.skipif` guards.

## Related

- [Source Module](../../../../agents/claude/README.md)
- [All Tests](../../README.md)
