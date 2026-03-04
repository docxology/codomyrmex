# Container Optimization Tests

**Version**: v1.1.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

Unit tests for the `container_optimization` module. Covers container image analysis, optimization suggestions, reporting, and resource tuning.

## Test Coverage

| Test Class | What It Tests |
|-----------|---------------|
| `TestContainerOptimizer` | Image analysis, optimization suggestions, and optimization reports |
| `TestResourceTuner` | Real container usage analysis and resource limit suggestions |

## Test Structure

```
tests/unit/container_optimization/
    __init__.py
    test_optimization.py
```

## Running Tests

```bash
# Run all tests for this module
uv run pytest src/codomyrmex/tests/unit/container_optimization/ -v

# Run with coverage
uv run pytest src/codomyrmex/tests/unit/container_optimization/ --cov=src/codomyrmex/container_optimization -v
```

## Test Policy

All tests follow the zero-mock policy: no `unittest.mock`, `MagicMock`, or `monkeypatch`.
External dependencies use `@pytest.mark.skipif` guards.

## Related

- [Source Module](../../../../container_optimization/README.md)
- [All Tests](../README.md)
