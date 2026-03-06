# Softmax Optimization Tests

**Version**: v1.1.4 | **Status**: Active | **Last Updated**: March 2026

## Overview

Unit tests for the `softmax_opt` module. Covers standard softmax (normalization, positivity, numerical stability, temperature scaling, 2D axis), log-softmax, and online softmax algorithm correctness.

## Test Coverage

| Test Class | What It Tests |
|-----------|---------------|
| `TestSoftmax` | Sum-to-one, all positive, numerical stability with large values, temperature, 2D axis |
| `TestLogSoftmax` | Log-softmax matches log of standard softmax |
| `TestOnlineSoftmax` | Online algorithm matches standard, sum-to-one verification |

## Test Structure

```
tests/unit/softmax_opt/
    __init__.py
    test_softmax_opt.py
```

## Running Tests

```bash
# Run all tests for this module
uv run pytest src/codomyrmex/tests/unit/softmax_opt/ -v

# Run with coverage
uv run pytest src/codomyrmex/tests/unit/softmax_opt/ --cov=src/codomyrmex/softmax_opt -v
```

## Test Policy

All tests follow the zero-mock policy: no `unittest.mock`, `MagicMock`, or `monkeypatch`.
External dependencies use `@pytest.mark.skipif` guards.

## Related

- [Source Module](../../../../softmax_opt/README.md)
- [All Tests](../README.md)
