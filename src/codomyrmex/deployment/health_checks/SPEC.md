# Health Checks -- Technical Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

Deployment health check framework. Defines an abstract `HealthCheck` base with five concrete implementations (HTTP, TCP, Command, Memory, Disk) and a `HealthChecker` aggregator that runs all checks and computes an overall status.

## Architecture

Template method pattern: `HealthCheck` (ABC) defines `check()` and provides a default `check_async()`. Concrete subclasses implement `check()`. `HealthChecker` collects multiple `HealthCheck` instances and runs them synchronously or asynchronously, then aggregates results.

## Key Classes

### `HealthCheck` (ABC)

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `check` | -- | `HealthCheckResult` | Abstract; perform the health check |
| `check_async` | -- | `HealthCheckResult` | Runs `check()` in a thread executor via `asyncio` |

Constructor: `(name: str, timeout: float = 5.0, critical: bool = True)`

### `HTTPHealthCheck`

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `url` | `str` | -- | Endpoint URL to check |
| `method` | `str` | `"GET"` | HTTP method |
| `expected_status` | `int` | `200` | Expected HTTP status code |
| `expected_body` | `str \| None` | `None` | Substring that must appear in response body |
| `headers` | `dict[str, str] \| None` | `None` | Custom request headers |

### `TCPHealthCheck`

| Parameter | Type | Description |
|-----------|------|-------------|
| `host` | `str` | Target hostname or IP |
| `port` | `int` | Target port number |

### `CommandHealthCheck`

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `command` | `list[str]` | -- | Command and arguments to execute |
| `expected_exit_code` | `int` | `0` | Expected process exit code |
| `expected_output` | `str \| None` | `None` | Substring that must appear in stdout |
| `timeout` | `float` | `10.0` | Command timeout in seconds |

### `MemoryHealthCheck`

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `warning_threshold` | `float` | `80.0` | Percent usage triggering DEGRADED |
| `critical_threshold` | `float` | `95.0` | Percent usage triggering UNHEALTHY |

### `DiskHealthCheck`

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `path` | `str` | `"/"` | Filesystem path to check |
| `warning_threshold` | `float` | `80.0` | Percent usage triggering DEGRADED |
| `critical_threshold` | `float` | `95.0` | Percent usage triggering UNHEALTHY |

### `HealthChecker`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `add_check` | `check: HealthCheck` | `HealthChecker` | Fluent API; appends check |
| `run_all` | -- | `AggregatedHealth` | Runs all checks synchronously |
| `run_all_async` | -- | `AggregatedHealth` | Runs all checks concurrently via `asyncio.gather` |

## Dependencies

- **Internal**: None
- **External**: Standard library (`asyncio`, `socket`, `subprocess`, `urllib.request`, `shutil`, `time`); `psutil` (optional)

## Constraints

- `HTTPHealthCheck` uses `urllib.request` (no external HTTP library required).
- `MemoryHealthCheck` returns `HealthStatus.UNKNOWN` when `psutil` is not installed.
- `CommandHealthCheck` captures up to 500 characters of stderr in details on failure.
- Overall status: UNHEALTHY if any critical check fails; DEGRADED if any non-critical check fails or any check is degraded.

## Error Handling

- All `check()` implementations catch broad `Exception` and return `HealthCheckResult` with UNHEALTHY status and the error message.
- `CommandHealthCheck` specifically catches `subprocess.TimeoutExpired`.
- `MemoryHealthCheck` catches `ImportError` for missing `psutil`.
