# Config Monitoring Tests

**Version**: v1.0.8 | **Status**: Active | **Last Updated**: March 2026

## Overview

Unit tests for the `config_monitoring` module. Covers configuration file monitoring, hash-based change detection, snapshot drift analysis, auditing, and file watcher callbacks.

## Test Coverage

| Test Class | What It Tests |
|-----------|---------------|
| `TestConfigurationMonitor` | File hash calculation, change detection, snapshots/drift, auditing, recent changes |
| `TestConfigWatcher` | File watcher callback invocation and file disappearance handling |

## Test Structure

```
tests/unit/config_monitoring/
    __init__.py
    test_config_monitor.py
```

## Running Tests

```bash
# Run all tests for this module
uv run pytest src/codomyrmex/tests/unit/config_monitoring/ -v

# Run with coverage
uv run pytest src/codomyrmex/tests/unit/config_monitoring/ --cov=src/codomyrmex/config_monitoring -v
```

## Test Policy

All tests follow the zero-mock policy: no `unittest.mock`, `MagicMock`, or `monkeypatch`.
External dependencies use `@pytest.mark.skipif` guards.

## Related

- [Source Module](../../../../config_monitoring/README.md)
- [All Tests](../README.md)
