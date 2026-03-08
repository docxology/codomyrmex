# Neural Tests

**Version**: v1.1.9 | **Status**: Active | **Last Updated**: March 2026

## Overview

Unit tests for the `neural` module. Covers scaled dot-product attention, multi-head attention, layer normalization, feed-forward networks, positional encoding, and embedding layers.

## Test Coverage

| Test Class | What It Tests |
|-----------|---------------|
| `TestScaledDotProductAttention` | Output shape, weight normalization, sqrt(dk) scaling, masking, single element |
| `TestMultiHeadAttention` | Output/weight shapes, cross-attention, d_model divisibility, single head, weight sum |
| `TestLayerNorm` | Output mean near zero, std near one, shape preservation, learnable params |
| `TestFeedForward` | Output shape, output differs from input |
| `TestPositionalEncoding` | Output shape, position uniqueness, determinism, additive encoding |
| `TestEmbedding` | Output shape, token uniqueness, same-token consistency |

## Test Structure

```
tests/unit/neural/
    __init__.py
    test_neural.py
```

## Running Tests

```bash
# Run all tests for this module
uv run pytest src/codomyrmex/tests/unit/neural/ -v

# Run with coverage
uv run pytest src/codomyrmex/tests/unit/neural/ --cov=src/codomyrmex/neural -v
```

## Test Policy

All tests follow the zero-mock policy: no `unittest.mock`, `MagicMock`, or `monkeypatch`.
External dependencies use `@pytest.mark.skipif` guards.

## Related

- [Source Module](../../../../neural/README.md)
- [All Tests](../README.md)
