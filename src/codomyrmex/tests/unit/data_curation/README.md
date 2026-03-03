# Data Curation Tests

**Version**: v1.0.8 | **Status**: Active | **Last Updated**: March 2026

## Overview

Unit tests for the `data_curation` module. Covers MinHash signatures, similarity estimation, shingling, LSH indexing, and data deduplication.

## Test Coverage

| Test Class | What It Tests |
|-----------|---------------|
| `TestMinHashSignature` | Signature length, dtype, determinism, empty/short text handling |
| `TestMinHashSimilarity` | Identical/different text similarity, symmetry, bounds |
| `TestMinHashShingle` | Whitespace normalization and case insensitivity |
| `TestLSHIndex` | Add/query, empty index, similar/different document candidates |
| `TestDataCurator` | Deduplication: removes duplicates, keeps unique, empty input, single document |

## Test Structure

```
tests/unit/data_curation/
    __init__.py
    test_data_curation.py
```

## Running Tests

```bash
# Run all tests for this module
uv run pytest src/codomyrmex/tests/unit/data_curation/ -v

# Run with coverage
uv run pytest src/codomyrmex/tests/unit/data_curation/ --cov=src/codomyrmex/data_curation -v
```

## Test Policy

All tests follow the zero-mock policy: no `unittest.mock`, `MagicMock`, or `monkeypatch`.
External dependencies use `@pytest.mark.skipif` guards.

## Related

- [Source Module](../../../../data_curation/README.md)
- [All Tests](../README.md)
