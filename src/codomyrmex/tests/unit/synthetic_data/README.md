# Synthetic Data Tests

**Version**: v1.1.9 | **Status**: Active | **Last Updated**: March 2026

## Overview

Unit tests for the `synthetic_data` module. Covers data schema, template-based generation, structured field generation (str, int, float, bool, choice, text), classification data, preference pair generation, and MCP tool integration.

## Test Coverage

| Test Class | What It Tests |
|-----------|---------------|
| `TestDataSchema` | Schema creation, default n_samples |
| `TestTemplateGenerator` | Template filling, determinism with seed, multiple templates |
| `TestSyntheticDataGeneratorStructured` | Str/int/float/bool/choice/text fields, determinism, multiple fields |
| `TestSyntheticDataGeneratorClassification` | Balanced/imbalanced, feature dimensionality, determinism, binary |
| `TestSyntheticDataGeneratorPreference` | Preference pair generation, quality score ranges, determinism |
| `TestSyntheticDataMCPTools` | generate_structured, generate_classification, generate_preference MCP tools |

## Test Structure

```
tests/unit/synthetic_data/
    __init__.py
    test_synthetic_data.py
```

## Running Tests

```bash
# Run all tests for this module
uv run pytest src/codomyrmex/tests/unit/synthetic_data/ -v

# Run with coverage
uv run pytest src/codomyrmex/tests/unit/synthetic_data/ --cov=src/codomyrmex/synthetic_data -v
```

## Test Policy

All tests follow the zero-mock policy: no `unittest.mock`, `MagicMock`, or `monkeypatch`.
External dependencies use `@pytest.mark.skipif` guards.

## Related

- [Source Module](../../../../synthetic_data/README.md)
- [All Tests](../README.md)
