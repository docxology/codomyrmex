# Soul Tests

**Version**: v1.0.8 | **Status**: Active | **Last Updated**: March 2026

## Overview

Unit tests for the `soul` module. Covers SoulAgent construction, memory stats, import error handling, MCP tools (soul_status, soul_init, soul_ask, soul_remember, soul_reset), and the HAS_SOUL flag.

## Test Coverage

| Test Class | What It Tests |
|-----------|---------------|
| `TestHasSoulFlag` | HAS_SOUL boolean flag verification |
| `TestSoulAgentWithoutLibrary` | Import error when soul library missing |
| `TestSoulAgentWithLibrary` | Constructor, memory_stats structure, nonexistent/existing files |
| `TestSoulStatus` | Status with missing/existing files, path reporting, partial existence |
| `TestSoulInit` | File creation, agent name, description, markdown format, no overwrite, defaults |
| `TestImportGuard` | soul_ask/remember/reset error when library missing |
| `TestSoulAskLive` | soul_ask success, memory persistence, no-remember mode, soul_remember, soul_reset |

## Test Structure

```
tests/unit/soul/
    __init__.py
    conftest.py       # Shared fixtures (soul_path, memory_path)
    test_agent.py     # SoulAgent class tests
    test_mcp_tools.py # MCP tool function tests
```

## Running Tests

```bash
# Run all tests for this module
uv run pytest src/codomyrmex/tests/unit/soul/ -v

# Run with coverage
uv run pytest src/codomyrmex/tests/unit/soul/ --cov=src/codomyrmex/soul -v
```

## Test Policy

All tests follow the zero-mock policy: no `unittest.mock`, `MagicMock`, or `monkeypatch`.
External dependencies use `@pytest.mark.skipif` guards.

## Related

- [Source Module](../../../../soul/README.md)
- [All Tests](../README.md)
