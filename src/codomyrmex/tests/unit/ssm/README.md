# SSM (State Space Model) Tests

**Version**: v1.1.9 | **Status**: Active | **Last Updated**: March 2026

## Overview

Unit tests for the `ssm` module. Covers selective SSM (output shape, causal property, state finiteness, dt_rank, batch independence), Mamba block (shape, finiteness, defaults, SiLU activation), stacked forward, and flash attention.

## Test Coverage

| Test Class | What It Tests |
|-----------|---------------|
| `TestSelectiveSSM` | Output shape, causal property, finite state, dt_rank default, batch independence |
| `TestMambaBlock` | Output shape/finiteness, callable, default/custom d_inner, SiLU activation |
| `TestMambaForward` | Stacked shape preservation, single layer, inferred d_model |
| `TestFlashAttention` | Flash vs standard match, output shape, causal mask, multihead, block_size=1 |

## Test Structure

```
tests/unit/ssm/
    __init__.py
    test_ssm.py
```

## Running Tests

```bash
# Run all tests for this module
uv run pytest src/codomyrmex/tests/unit/ssm/ -v

# Run with coverage
uv run pytest src/codomyrmex/tests/unit/ssm/ --cov=src/codomyrmex/ssm -v
```

## Test Policy

All tests follow the zero-mock policy: no `unittest.mock`, `MagicMock`, or `monkeypatch`.
External dependencies use `@pytest.mark.skipif` guards.

## Related

- [Source Module](../../../../ssm/README.md)
- [All Tests](../README.md)
