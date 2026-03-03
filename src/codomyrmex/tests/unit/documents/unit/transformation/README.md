# Documents / Transformation Tests

**Version**: v1.0.8 | **Status**: Active | **Last Updated**: March 2026

## Overview

Unit tests for the document transformation sub-module. Covers JSON-to-YAML conversion, text document merging, and section-based splitting.

## Test Coverage

| Test Class | What It Tests |
|-----------|---------------|
| `TestTransformation` | JSON-to-YAML conversion, text document merging, section splitting |

## Test Structure

```
tests/unit/documents/unit/transformation/
    __init__.py
    test_transformation.py
```

## Running Tests

```bash
# Run all tests for this module
uv run pytest src/codomyrmex/tests/unit/documents/unit/transformation/ -v

# Run with coverage
uv run pytest src/codomyrmex/tests/unit/documents/unit/transformation/ --cov=src/codomyrmex/documents -v
```

## Test Policy

All tests follow the zero-mock policy: no `unittest.mock`, `MagicMock`, or `monkeypatch`.
External dependencies use `@pytest.mark.skipif` guards.

## Related

- [Source Module](../../../../documents/README.md)
- [All Tests](../../../README.md)
