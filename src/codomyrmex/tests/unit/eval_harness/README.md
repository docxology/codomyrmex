# Eval Harness Tests

**Version**: v1.1.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

Unit tests for the `eval_harness` module. Covers answer normalization, exact match and F1 metrics, evaluation dataclasses, and harness integration with identity/custom model functions.

## Test Coverage

| Test Class | What It Tests |
|-----------|---------------|
| `TestNormalizeAnswer` | Whitespace stripping, lowercasing, combined normalization |
| `TestExactMatchMetric` | Perfect/partial/no match, case/whitespace insensitivity |
| `TestF1Metric` | Perfect/zero/partial F1, empty prediction, case insensitivity |
| `TestEvalDataclasses` | EvalTask defaults and EvalResult fields |
| `TestEvalHarness` | Identity model evaluation, case-insensitive matching, custom model functions |

## Test Structure

```
tests/unit/eval_harness/
    __init__.py
    test_eval_harness.py
```

## Running Tests

```bash
# Run all tests for this module
uv run pytest src/codomyrmex/tests/unit/eval_harness/ -v

# Run with coverage
uv run pytest src/codomyrmex/tests/unit/eval_harness/ --cov=src/codomyrmex/eval_harness -v
```

## Test Policy

All tests follow the zero-mock policy: no `unittest.mock`, `MagicMock`, or `monkeypatch`.
External dependencies use `@pytest.mark.skipif` guards.

## Related

- [Source Module](../../../../eval_harness/README.md)
- [All Tests](../README.md)
