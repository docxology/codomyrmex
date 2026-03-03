# DPO (Direct Preference Optimization) Tests

**Version**: v1.0.8 | **Status**: Active | **Last Updated**: March 2026

## Overview

Unit tests for the `dpo` module. Covers log-probability computation, DPO loss formula correctness, accuracy metrics, the DPOLoss callable class, and MCP tool integration.

## Test Coverage

| Test Class | What It Tests |
|-----------|---------------|
| `TestComputeLogProbs` | Log-prob shape, non-positivity, ignore index, high logit behavior |
| `TestComputeDPOLoss` | Loss formula, winner/loser comparison, accuracy, result keys, beta storage |
| `TestDPOLoss` | History tracking, reset, callable return structure |
| `TestMCPTool` | dpo_compute_loss MCP tool and metadata |

## Test Structure

```
tests/unit/dpo/
    __init__.py
    test_dpo.py
```

## Running Tests

```bash
# Run all tests for this module
uv run pytest src/codomyrmex/tests/unit/dpo/ -v

# Run with coverage
uv run pytest src/codomyrmex/tests/unit/dpo/ --cov=src/codomyrmex/dpo -v
```

## Test Policy

All tests follow the zero-mock policy: no `unittest.mock`, `MagicMock`, or `monkeypatch`.
External dependencies use `@pytest.mark.skipif` guards.

## Related

- [Source Module](../../../../dpo/README.md)
- [All Tests](../README.md)
