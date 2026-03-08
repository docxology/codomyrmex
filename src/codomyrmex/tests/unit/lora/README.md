# LoRA Tests

**Version**: v1.1.9 | **Status**: Active | **Last Updated**: March 2026

## Overview

Unit tests for the `lora` module. Covers LoRA configuration and scaling, layer initialization (B=0, A/B shapes), forward pass formula verification, merge/unmerge operations, rank and parameter efficiency, and MCP tool integration.

## Test Coverage

| Test Class | What It Tests |
|-----------|---------------|
| `TestLoRAConfig` | Default config values, scaling property computation |
| `TestLoRALayerInit` | B zero-init, initial delta=0, A/B shapes, W0 copy |
| `TestLoRALayerForward` | Forward pass formula (W0*x + scaling*B*A*x), initial equals base |
| `TestLoRAMerge` | Merge changes W0, merged=unmerged equivalence, idempotent merge, unmerge restore |
| `TestLoRARankAndParams` | Rank preservation, parameter count reduction, initial effective rank=0 |
| `TestConvenienceFunctions` | apply_lora and merge_lora convenience APIs |
| `TestMCPTool` | lora_apply MCP tool and metadata |

## Test Structure

```
tests/unit/lora/
    __init__.py
    test_lora.py
```

## Running Tests

```bash
# Run all tests for this module
uv run pytest src/codomyrmex/tests/unit/lora/ -v

# Run with coverage
uv run pytest src/codomyrmex/tests/unit/lora/ --cov=src/codomyrmex/lora -v
```

## Test Policy

All tests follow the zero-mock policy: no `unittest.mock`, `MagicMock`, or `monkeypatch`.
External dependencies use `@pytest.mark.skipif` guards.

## Related

- [Source Module](../../../../lora/README.md)
- [All Tests](../README.md)
