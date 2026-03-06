# Interpretability Tests

**Version**: v1.1.4 | **Status**: Active | **Last Updated**: March 2026

## Overview

Unit tests for the `interpretability` module. Covers sparse autoencoder initialization, encode/decode operations, loss computation, training steps, feature analysis, and the train_sae convenience function.

## Test Coverage

| Test Class | What It Tests |
|-----------|---------------|
| `TestSparseAutoencoderInit` | Dimensions, weight shapes, decoder normalization, lambda_l1 |
| `TestSparseAutoencoderEncodeDecode` | Encode shape, non-negativity, sparsity, decode shape, forward pass |
| `TestSparseAutoencoderLoss` | Loss components, total loss sum, non-negative reconstruction/sparsity, sparsity ratio |
| `TestSparseAutoencoderTraining` | Train step loss, decoder normalization, weight changes over steps |
| `TestTrainSAE` | train_sae return type, default overcomplete ratio, determinism |
| `TestAnalyzeFeatures` | Feature analysis keys, top features sorting, limit to 10, sparsity ratio |

## Test Structure

```
tests/unit/interpretability/
    __init__.py
    test_interpretability.py
```

## Running Tests

```bash
# Run all tests for this module
uv run pytest src/codomyrmex/tests/unit/interpretability/ -v

# Run with coverage
uv run pytest src/codomyrmex/tests/unit/interpretability/ --cov=src/codomyrmex/interpretability -v
```

## Test Policy

All tests follow the zero-mock policy: no `unittest.mock`, `MagicMock`, or `monkeypatch`.
External dependencies use `@pytest.mark.skipif` guards.

## Related

- [Source Module](../../../../interpretability/README.md)
- [All Tests](../README.md)
