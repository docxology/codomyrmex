# Operating System Tests

**Version**: v1.0.8 | **Status**: Active | **Last Updated**: March 2026

## Overview

Unit tests for the `operating_system` module. Covers platform detection, provider dispatch, system info, process listing, disk usage, command execution, and environment variables.

## Test Coverage

| Test Class | What It Tests |
|-----------|---------------|
| `TestPlatformDetection` | Platform enum return, matches sys.platform |
| `TestProviderDispatch` | Provider subclass, caching, class name matches platform |
| `TestSystemInfo` | System info retrieval, to_dict, memory > 0, platform version |
| `TestProcesses` | Process listing, PID/name fields, to_dict |
| `TestDiskUsage` | Disk usage listing, mountpoint, total > 0, to_dict |
| `TestCommandExecution` | Echo execution, duration, bad command error, result to_dict |
| `TestEnvironmentVariables` | All env vars retrieval, PATH in env |

## Test Structure

```
tests/unit/operating_system/
    __init__.py
    test_operating_system.py
```

## Running Tests

```bash
# Run all tests for this module
uv run pytest src/codomyrmex/tests/unit/operating_system/ -v

# Run with coverage
uv run pytest src/codomyrmex/tests/unit/operating_system/ --cov=src/codomyrmex/operating_system -v
```

## Test Policy

All tests follow the zero-mock policy: no `unittest.mock`, `MagicMock`, or `monkeypatch`.
External dependencies use `@pytest.mark.skipif` guards.

## Related

- [Source Module](../../../../operating_system/README.md)
- [All Tests](../README.md)
