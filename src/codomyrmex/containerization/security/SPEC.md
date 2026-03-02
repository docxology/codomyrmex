# Security -- Technical Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

Provides container security scanning via Trivy CLI and container performance metrics collection via Docker CLI. Two scanner classes (`SecurityScanner`, `ContainerSecurityScanner`) wrap Trivy for vulnerability detection with JSON output parsing. `ContainerOptimizer` collects real-time container metrics via `docker stats` and produces resource optimization recommendations via `docker inspect`.

## Architecture

Two-file design. `security_scanner.py` contains two scanner classes backed by the Trivy CLI (located via `shutil.which("trivy")`), shared helper functions `_trivy_cli()` and `_parse_trivy_results()`, and data models for vulnerabilities and scan results. `performance_optimizer.py` contains `ContainerOptimizer` (uses Docker CLI) and `PerformanceOptimizer` (stub that raises `NotImplementedError`).

## Key Classes and Methods

### SecurityScanner (`security_scanner.py`)

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `scan` | `image: str` | `dict` | Scan image via `trivy image --format json`; returns image, status, vulnerabilities list |

### ContainerSecurityScanner (`security_scanner.py`)

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `__init__` | `config: dict or None` | -- | Initialize with optional config; maintains `_scan_history` |
| `scan_image` | `image: str, **kwargs` | `SecurityScanResult` | Scan with optional `severity_filter` list; sets `passed=False` if CRITICAL or HIGH found |

### Helper Functions (`security_scanner.py`)

| Function | Parameters | Returns | Description |
|----------|-----------|---------|-------------|
| `_trivy_cli` | (none) | `str` | Locate Trivy via `shutil.which`; raises `NotImplementedError` if missing |
| `_parse_trivy_results` | `data: dict` | `list[Vulnerability]` | Parse Trivy JSON `Results[].Vulnerabilities[]` into `Vulnerability` objects |

### ContainerOptimizer (`performance_optimizer.py`)

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `__init__` | `config: dict or None` | -- | Initialize with optional config; maintains `_metrics_history` |
| `collect_metrics` | `container_id: str` | `ContainerMetrics` | Run `docker stats --no-stream` and parse CPU, memory, network, disk IO |
| `optimize_resources` | `container_id: str` | `dict` | Run `docker inspect` and recommend CPU/memory limits |

### PerformanceOptimizer (`performance_optimizer.py`)

Stub class. `optimize()` raises `NotImplementedError` directing users to `ContainerOptimizer`.

### Data Models

#### VulnerabilitySeverity (enum)

Values: `CRITICAL`, `HIGH`, `MEDIUM`, `LOW`, `INFO`.

#### Vulnerability (dataclass)

`id, severity: VulnerabilitySeverity, title, description, package, version, fixed_version, cve_ids`.

#### SecurityScanResult (dataclass)

`image, scan_time, vulnerabilities, passed, error, metadata`. Properties: `critical_count`, `high_count`. Method: `summary()` returning severity counts.

#### ContainerMetrics (dataclass)

`container_id, cpu_percent, memory_usage_mb, memory_limit_mb, network_io_mb, disk_io_mb, timestamp`. Property: `memory_percent`. Method: `to_dict()`.

## Dependencies

- **Internal**: (none for security_scanner.py); `codomyrmex.logging_monitoring` (implicit via scanner classes)
- **External**: Trivy CLI (runtime), Docker CLI (runtime for performance_optimizer), `json`, `shutil`, `subprocess`

## Constraints

- Both scanner classes locate Trivy via `shutil.which("trivy")`; raise `NotImplementedError` if not installed.
- `ContainerSecurityScanner.scan_image` sets `passed=False` when any CRITICAL or HIGH vulnerability is found.
- Trivy subprocess has a 120-second timeout.
- `_parse_trivy_results` maps Trivy's `"UNKNOWN"` severity to `VulnerabilitySeverity.INFO`.
- `ContainerOptimizer.collect_metrics` parses `docker stats` JSON output with unit conversions (GiB, MiB, GB, MB, kB, B to MB).
- `ContainerOptimizer.optimize_resources` uses `docker inspect --format '{{json .HostConfig}}'` to read CPU shares and memory limits.
- Docker CLI subprocess timeout is 15 seconds for stats and 10 seconds for inspect.
- `PerformanceOptimizer.optimize()` is a stub that always raises `NotImplementedError`.

## Error Handling

- `SecurityScanner.scan` raises `NotImplementedError` if Trivy fails (`CalledProcessError`).
- `ContainerSecurityScanner.scan_image` returns a `SecurityScanResult` with `passed=False` and `error` message on subprocess failure instead of raising.
- `ContainerOptimizer.collect_metrics` raises `NotImplementedError` for missing Docker CLI, subprocess failures, or JSON parse errors.
- `ContainerOptimizer.optimize_resources` raises `NotImplementedError` for missing Docker CLI or subprocess failures.
