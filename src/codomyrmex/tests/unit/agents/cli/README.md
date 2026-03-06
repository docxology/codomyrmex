# Agents / CLI Handlers Tests

**Version**: v1.1.4 | **Status**: Active | **Last Updated**: March 2026

## Overview

Unit tests for the `agents/cli` sub-module. Covers CLI handler functions for agent info, setup, execute, stream, and Jules-specific handlers.

## Test Coverage

| Test Class | What It Tests |
|-----------|---------------|
| `TestParseContext` | JSON context string parsing (valid, invalid, nested) |
| `TestCreateAgentRequest` | Agent request creation from CLI args |
| `TestHandleInfo` | Info handler output (verbose, JSON, text formats) |
| `TestHandleAgentSetupNoneClient` | Setup handler with None client guard |
| `TestHandleAgentTestNoneClient` | Test handler with None client guard |
| `TestAgentExecuteNoneGuard` | Execute/stream None client guards |
| `TestJulesHandlers` | Jules-specific execute, stream, and check handlers |

## Test Structure

```
tests/unit/agents/cli/
    __init__.py
    test_handlers.py
```

## Running Tests

```bash
# Run all tests for this module
uv run pytest src/codomyrmex/tests/unit/agents/cli/ -v

# Run with coverage
uv run pytest src/codomyrmex/tests/unit/agents/cli/ --cov=src/codomyrmex/agents/cli -v
```

## Test Policy

All tests follow the zero-mock policy: no `unittest.mock`, `MagicMock`, or `monkeypatch`.
External dependencies use `@pytest.mark.skipif` guards.

## Related

- [Source Module](../../../../agents/cli/README.md)
- [All Tests](../../README.md)
