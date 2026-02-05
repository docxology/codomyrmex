# deployment/health_checks

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

Deployment health check implementations. Provides a pluggable health check framework for monitoring service availability, resource utilization, and endpoint responsiveness. Supports HTTP, TCP, command-based, memory, and disk checks with both synchronous and asynchronous execution.

## Key Exports

### Enums

- **`HealthStatus`** -- Health check status levels: `HEALTHY`, `UNHEALTHY`, `DEGRADED`, `UNKNOWN`

### Data Classes

- **`HealthCheckResult`** -- Result of a single health check containing name, status, message, latency in milliseconds, timestamp, and additional details. Includes `to_dict()` serialization
- **`AggregatedHealth`** -- Aggregated results from multiple checks with overall status, individual check results, and computed `healthy_count` / `unhealthy_count` properties

### Abstract Base Class

- **`HealthCheck`** -- ABC for health checks with configurable name, timeout, and critical flag. Provides `check()` (sync) and `check_async()` (async via executor) interfaces

### Check Implementations

- **`HTTPHealthCheck`** -- HTTP/HTTPS endpoint check supporting configurable URL, method, expected status code, expected body content, and custom headers
- **`TCPHealthCheck`** -- TCP port connectivity check with configurable host, port, and socket timeout
- **`CommandHealthCheck`** -- Shell command execution check verifying exit code and optional output matching
- **`MemoryHealthCheck`** -- System memory usage check using `psutil` with configurable warning (default 80%) and critical (default 95%) thresholds. Reports total/available GB and percent used
- **`DiskHealthCheck`** -- Disk space usage check using `shutil.disk_usage` with configurable path and warning/critical thresholds. Reports total/free GB and percent used

### Orchestrator

- **`HealthChecker`** -- Manages multiple health checks with `add_check()` (fluent API), `run_all()` (sync), and `run_all_async()` (parallel async via `asyncio.gather`). Determines overall status considering critical vs non-critical check distinctions

## Directory Contents

- `__init__.py` - Health check framework: ABC, implementations, aggregator, and status enum (497 lines)
- `py.typed` - PEP 561 typing marker
- `SPEC.md` - Module specification
- `AGENTS.md` - Agent integration documentation
- `PAI.md` - PAI integration notes

## Navigation

- **Parent Module**: [deployment](../README.md)
- **Project Root**: [codomyrmex](../../../../README.md)
