# Quantization Tests

**Version**: v1.1.9 | **Status**: Active | **Last Updated**: March 2026

## Overview

Unit tests for the `quantization` module. Covers INT8 quantization (symmetric/asymmetric, scale, zero-point, round-trip), INT8 quantizer calibration, and FP4 quantization (packing, compression ratio, shape preservation).

## Test Coverage

| Test Class | What It Tests |
|-----------|---------------|
| `TestInt8Quantization` | INT8 range, asymmetric/symmetric round-trip, zero-point, scale, dtype, large range, zeros |
| `TestInt8Quantizer` | Calibrated quantizer, calibrate sets state, auto-calibrate, symmetric mode |
| `TestFP4Quantization` | FP4 round-trip shape, dtype, even/odd packing, scale, size/shape match, zeros, compression ratio |

## Test Structure

```
tests/unit/quantization/
    __init__.py
    test_quantization.py
```

## Running Tests

```bash
# Run all tests for this module
uv run pytest src/codomyrmex/tests/unit/quantization/ -v

# Run with coverage
uv run pytest src/codomyrmex/tests/unit/quantization/ --cov=src/codomyrmex/quantization -v
```

## Test Policy

All tests follow the zero-mock policy: no `unittest.mock`, `MagicMock`, or `monkeypatch`.
External dependencies use `@pytest.mark.skipif` guards.

## Related

- [Source Module](../../../../quantization/README.md)
- [All Tests](../README.md)
