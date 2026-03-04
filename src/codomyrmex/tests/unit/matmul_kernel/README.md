# MatMul Kernel Tests

**Version**: v1.1.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

Unit tests for the `matmul_kernel` module. Covers tiled matrix multiplication, batched matrix multiplication, and FLOPS calculation.

## Test Coverage

| Test Class | What It Tests |
|-----------|---------------|
| `TestTiledMatmul` | Small square, rectangular, output shape, tile size variation, identity matrix |
| `TestBatchedMatmul` | Batched shape and correctness verification |
| `TestFlops` | FLOPS formula validation |

## Test Structure

```
tests/unit/matmul_kernel/
    __init__.py
    test_matmul_kernel.py
```

## Running Tests

```bash
# Run all tests for this module
uv run pytest src/codomyrmex/tests/unit/matmul_kernel/ -v

# Run with coverage
uv run pytest src/codomyrmex/tests/unit/matmul_kernel/ --cov=src/codomyrmex/matmul_kernel -v
```

## Test Policy

All tests follow the zero-mock policy: no `unittest.mock`, `MagicMock`, or `monkeypatch`.
External dependencies use `@pytest.mark.skipif` guards.

## Related

- [Source Module](../../../../matmul_kernel/README.md)
- [All Tests](../README.md)
