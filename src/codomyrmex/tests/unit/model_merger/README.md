# Model Merger Tests

**Version**: v1.1.4 | **Status**: Active | **Last Updated**: March 2026

## Overview

Unit tests for the `model_merger` module. Covers SLERP interpolation, linear interpolation, model soup (uniform/weighted averaging), the ModelMerger class, and MCP tool integration.

## Test Coverage

| Test Class | What It Tests |
|-----------|---------------|
| `TestSlerp` | SLERP at t=0/0.5/1, shape preservation, parallel vector fallback, magnitude interpolation |
| `TestLinearInterpolate` | Linear midpoint, alpha=0/1, missing key handling, multiple keys |
| `TestModelSoup` | Uniform average, weighted average, single model, empty raises, 2D params |
| `TestModelMerger` | SLERP method, linear method, unknown method raises, missing key preservation |
| `TestModelMergerMCPTools` | merge_models and create_model_soup MCP tools |

## Test Structure

```
tests/unit/model_merger/
    __init__.py
    test_model_merger.py
```

## Running Tests

```bash
# Run all tests for this module
uv run pytest src/codomyrmex/tests/unit/model_merger/ -v

# Run with coverage
uv run pytest src/codomyrmex/tests/unit/model_merger/ --cov=src/codomyrmex/model_merger -v
```

## Test Policy

All tests follow the zero-mock policy: no `unittest.mock`, `MagicMock`, or `monkeypatch`.
External dependencies use `@pytest.mark.skipif` guards.

## Related

- [Source Module](../../../../model_merger/README.md)
- [All Tests](../README.md)
