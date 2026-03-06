# Synthetic Data Tests -- Agent Coordination

**Version**: v1.1.4 | **Status**: Active | **Last Updated**: March 2026

## Overview

Test suite for the `synthetic_data` module, implementing the zero-mock testing policy.

## Running Tests

```bash
uv run pytest src/codomyrmex/tests/unit/synthetic_data/ -v
```

## Test Markers

| Marker | Usage |
|--------|-------|
| `@pytest.mark.unit` | All tests in this suite |
| `@pytest.mark.skipif` | Tests requiring external services or optional SDKs |

## Agent Instructions

1. Run this test suite after any changes to `src/codomyrmex/synthetic_data/`
2. Tests must pass before merging changes to main
3. Check for `@pytest.mark.skipif` guards before adding new tests
4. Follow the zero-mock policy: no `unittest.mock`, `MagicMock`, or `monkeypatch`

## Navigation

- [README.md](README.md) | [SPEC.md](SPEC.md) | [Source](../../../../synthetic_data/)
