# Demos Tests

**Version**: v1.1.9 | **Status**: Active | **Last Updated**: March 2026

## Overview

Unit tests for the `demos` module. Covers demo example validation and demo registry operations (register, list, discover, run).

## Test Coverage

| Test Function | What It Tests |
|--------------|---------------|
| `test_example_addition` | Basic generated example validation |
| `test_registry_register_and_list` | Demo registry registration and listing |
| `test_run_callable_demo` | Running callable demos |
| `test_discover_and_run_script_demo` | Script demo discovery and execution |
| `test_run_nonexistent_demo` | Error handling for missing demos |

## Test Structure

```
tests/unit/demos/
    __init__.py
    test_generated_example.py
    test_registry.py
```

## Running Tests

```bash
# Run all tests for this module
uv run pytest src/codomyrmex/tests/unit/demos/ -v

# Run with coverage
uv run pytest src/codomyrmex/tests/unit/demos/ --cov=src/codomyrmex/demos -v
```

## Test Policy

All tests follow the zero-mock policy: no `unittest.mock`, `MagicMock`, or `monkeypatch`.
External dependencies use `@pytest.mark.skipif` guards.

## Related

- [Source Module](../../../../demos/README.md)
- [All Tests](../README.md)
