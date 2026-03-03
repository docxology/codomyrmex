# NAS (Neural Architecture Search) Tests

**Version**: v1.0.8 | **Status**: Active | **Last Updated**: March 2026

## Overview

Unit tests for the `nas` module. Covers architecture configuration, search space constraints, random and evolutionary search strategies, mutation, and MCP tool integration.

## Test Coverage

| Test Class | What It Tests |
|-----------|---------------|
| `TestArchConfig` | Parameter estimation, scaling with layers/width, default params dict |
| `TestNASSearchSpace` | Sample type, constraint validation, determinism with seed, custom space |
| `TestNASSearcher` | Random/evolutionary search, history tracking, best raises on empty, max score |
| `TestConvenienceFunctions` | random_search and evolutionary_search wrapper functions |
| `TestMutation` | Mutation produces valid config and changes at least one field |
| `TestMCPTools` | sample_architecture MCP tool |

## Test Structure

```
tests/unit/nas/
    __init__.py
    test_nas.py
```

## Running Tests

```bash
# Run all tests for this module
uv run pytest src/codomyrmex/tests/unit/nas/ -v

# Run with coverage
uv run pytest src/codomyrmex/tests/unit/nas/ --cov=src/codomyrmex/nas -v
```

## Test Policy

All tests follow the zero-mock policy: no `unittest.mock`, `MagicMock`, or `monkeypatch`.
External dependencies use `@pytest.mark.skipif` guards.

## Related

- [Source Module](../../../../nas/README.md)
- [All Tests](../README.md)
