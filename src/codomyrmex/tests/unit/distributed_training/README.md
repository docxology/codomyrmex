# Distributed Training Tests

**Version**: v1.1.9 | **Status**: Active | **Last Updated**: March 2026

## Overview

Unit tests for the `distributed_training` module. Covers FSDP sharding, collective operations (all-gather, reduce-scatter, all-reduce), FSDP step simulation, and MCP tool integration.

## Test Coverage

| Test Class | What It Tests |
|-----------|---------------|
| `TestFSDPShard` | Shard construction, grad shard defaults, device ID storage |
| `TestAllGather` | All-gather concatenation, size preservation, single shard |
| `TestReduceScatter` | Reduce-scatter shard count, averaging, element coverage |
| `TestAllReduce` | All-reduce sum and mean operations, broadcast count, independent copies |
| `TestSimulateFSDPStep` | Parameter update, shard coverage, device IDs, grad shard correctness, zero gradients |
| `TestMCPTool` | fsdp_simulate_step MCP tool and metadata |

## Test Structure

```
tests/unit/distributed_training/
    __init__.py
    test_distributed_training.py
```

## Running Tests

```bash
# Run all tests for this module
uv run pytest src/codomyrmex/tests/unit/distributed_training/ -v

# Run with coverage
uv run pytest src/codomyrmex/tests/unit/distributed_training/ --cov=src/codomyrmex/distributed_training -v
```

## Test Policy

All tests follow the zero-mock policy: no `unittest.mock`, `MagicMock`, or `monkeypatch`.
External dependencies use `@pytest.mark.skipif` guards.

## Related

- [Source Module](../../../../distributed_training/README.md)
- [All Tests](../README.md)
