# Autograd Tests

**Version**: v1.0.8 | **Status**: Active | **Last Updated**: March 2026

## Overview

Unit tests for the `autograd` module. Covers forward-mode arithmetic (add, mul, pow, neg, sub, div, exp), reverse-mode backward pass (chain rule, gradient accumulation), and activation functions (relu, tanh, sigmoid).

## Test Coverage

| Test Class | What It Tests |
|-----------|---------------|
| `TestValueForward` | Forward arithmetic: add, mul, pow, neg, sub, div, radd, rmul, rsub, rtruediv, exp, repr |
| `TestValueBackward` | Backward pass: gradients for add, mul, pow, chain rule, shared nodes, deep chains |
| `TestActivationsScalar` | Activation functions: relu (positive/negative), tanh (zero/backward), sigmoid |

## Test Structure

```
tests/unit/autograd/
    __init__.py
    test_autograd.py
```

## Running Tests

```bash
# Run all tests for this module
uv run pytest src/codomyrmex/tests/unit/autograd/ -v

# Run with coverage
uv run pytest src/codomyrmex/tests/unit/autograd/ --cov=src/codomyrmex/autograd -v
```

## Test Policy

All tests follow the zero-mock policy: no `unittest.mock`, `MagicMock`, or `monkeypatch`.
External dependencies use `@pytest.mark.skipif` guards.

## Related

- [Source Module](../../../../autograd/README.md)
- [All Tests](../README.md)
