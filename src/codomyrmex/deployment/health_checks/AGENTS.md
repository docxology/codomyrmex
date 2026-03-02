# Codomyrmex Agents — src/codomyrmex/deployment/health_checks

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose

Health check implementations for deployment validation. Provides an abstract `HealthCheck` base class with concrete implementations for HTTP endpoints, TCP ports, shell commands, memory usage, and disk space. A `HealthChecker` aggregates multiple checks into an overall health status.

## Key Components

| File | Class / Function | Role |
|------|-----------------|------|
| `__init__.py` | `HealthStatus` | Enum: HEALTHY, UNHEALTHY, DEGRADED, UNKNOWN |
| `__init__.py` | `HealthCheckResult` | Dataclass: name, status, message, latency_ms, timestamp, details; `to_dict()` serialization |
| `__init__.py` | `AggregatedHealth` | Dataclass: overall_status, checks list; properties `healthy_count`, `unhealthy_count`; `to_dict()` |
| `__init__.py` | `HealthCheck` | ABC: `check()` abstract, `check_async()` default (runs check in executor); constructor takes name, timeout, critical flag |
| `__init__.py` | `HTTPHealthCheck` | Checks HTTP endpoint: url, method, expected_status, expected_body, headers |
| `__init__.py` | `TCPHealthCheck` | Checks TCP port connectivity: host, port |
| `__init__.py` | `CommandHealthCheck` | Runs shell command: command list, expected_exit_code, expected_output |
| `__init__.py` | `MemoryHealthCheck` | Checks system memory via `psutil`: warning_threshold (80%), critical_threshold (95%) |
| `__init__.py` | `DiskHealthCheck` | Checks disk usage via `shutil.disk_usage`: path, warning_threshold (80%), critical_threshold (95%) |
| `__init__.py` | `HealthChecker` | Aggregator: `add_check(check)`, `run_all()`, `run_all_async()`; determines overall status from critical checks |

## Operating Contracts

- `HealthCheck.check_async()` runs the synchronous `check()` method in a thread executor by default.
- `HealthChecker._determine_overall_status` returns UNHEALTHY if any critical check is unhealthy; DEGRADED if any non-critical check is unhealthy or any check is degraded; HEALTHY otherwise.
- `MemoryHealthCheck` requires `psutil`; returns UNKNOWN status if the package is not installed.
- All check implementations measure and report `latency_ms`.
- Errors must be logged via `logging_monitoring` before re-raising.

## Integration Points

- **Depends on**: Standard library (`asyncio`, `socket`, `subprocess`, `urllib.request`, `shutil`, `time`); `psutil` (optional, for `MemoryHealthCheck`)
- **Used by**: `codomyrmex.deployment.manager` (DeploymentOrchestrator uses HealthChecker for post-deploy verification)

## Navigation

- **Parent**: [deployment](../README.md)
- **Root**: [Root](../../../../README.md)
