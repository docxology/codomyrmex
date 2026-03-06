# Distillation Tests

**Version**: v1.1.4 | **Status**: Active | **Last Updated**: March 2026

## Overview

Unit tests for the `distillation` module. Covers soft label computation, KL divergence and cross-entropy distillation loss, alpha blending, teacher accuracy, and MCP tool integration.

## Test Coverage

| Test Class | What It Tests |
|-----------|---------------|
| `TestSoftLabels` | Soft label normalization, temperature scaling, probability positivity |
| `TestDistillationLoss` | KL loss, CE loss, total loss composition, alpha=0/1 edge cases, teacher accuracy |
| `TestDistillationLossClass` | DistillationLoss callable class defaults and return structure |
| `TestMCPTool` | distillation_compute_loss MCP tool and metadata |

## Test Structure

```
tests/unit/distillation/
    __init__.py
    test_distillation.py
```

## Running Tests

```bash
# Run all tests for this module
uv run pytest src/codomyrmex/tests/unit/distillation/ -v

# Run with coverage
uv run pytest src/codomyrmex/tests/unit/distillation/ --cov=src/codomyrmex/distillation -v
```

## Test Policy

All tests follow the zero-mock policy: no `unittest.mock`, `MagicMock`, or `monkeypatch`.
External dependencies use `@pytest.mark.skipif` guards.

## Related

- [Source Module](../../../../distillation/README.md)
- [All Tests](../README.md)
