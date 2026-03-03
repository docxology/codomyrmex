# Semantic Router Tests

**Version**: v1.0.8 | **Status**: Active | **Last Updated**: March 2026

## Overview

Unit tests for the `semantic_router` module. Covers route registration, similarity-based routing, batch routing, embedding normalization and determinism, RouteMatch fields, and MCP tool integration.

## Test Coverage

| Test Class | What It Tests |
|-----------|---------------|
| `TestSemanticRouterBasic` | Route registration, embedding computation, empty router no-match |
| `TestSemanticRouterRouting` | Similar text matching, exact utterance, score bounds, threshold, determinism |
| `TestSemanticRouterBatch` | Batch routing returns list, empty input handling |
| `TestEmbedding` | Embedding normalization, shape, determinism, case insensitivity |
| `TestRouteMatch` | RouteMatch dataclass fields |
| `TestMCPTools` | semantic_router_route MCP tool, metadata, custom routes |

## Test Structure

```
tests/unit/semantic_router/
    __init__.py
    test_semantic_router.py
```

## Running Tests

```bash
# Run all tests for this module
uv run pytest src/codomyrmex/tests/unit/semantic_router/ -v

# Run with coverage
uv run pytest src/codomyrmex/tests/unit/semantic_router/ --cov=src/codomyrmex/semantic_router -v
```

## Test Policy

All tests follow the zero-mock policy: no `unittest.mock`, `MagicMock`, or `monkeypatch`.
External dependencies use `@pytest.mark.skipif` guards.

## Related

- [Source Module](../../../../semantic_router/README.md)
- [All Tests](../README.md)
