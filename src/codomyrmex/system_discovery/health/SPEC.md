# Health Checker -- Technical Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

Module health verification system that probes importability, dependency satisfaction, and documentation completeness across Codomyrmex modules. Produces per-module and aggregate health reports.

## Architecture

```
HealthChecker(discovery_engine: DiscoveryEngine)
  +-- check(module_name) -> HealthResult
  +-- check_all() -> HealthReport
  +-- register_probe(probe: HealthProbe)

HealthResult
  +-- module: str
  +-- status: "healthy" | "degraded" | "unhealthy"
  +-- import_ok: bool
  +-- deps_satisfied: bool
  +-- rasp_complete: bool
  +-- details: dict

HealthReport
  +-- results: list[HealthResult]
  +-- score: float (0.0-100.0)
  +-- healthy_count / degraded_count / unhealthy_count
  +-- summary() -> str
```

## Key Classes

### HealthResult

| Field | Type | Notes |
|-------|------|-------|
| `module` | `str` | Module name |
| `status` | `str` | `"healthy"`, `"degraded"`, or `"unhealthy"` |
| `import_ok` | `bool` | Whether `importlib.import_module` succeeds |
| `deps_satisfied` | `bool` | All required deps importable |
| `rasp_complete` | `bool` | All 4 RASP docs present |
| `details` | `dict` | Error messages, missing deps list |

### HealthChecker Methods

| Method | Returns | Description |
|--------|---------|-------------|
| `check(module_name)` | `HealthResult` | Probe single module |
| `check_all()` | `HealthReport` | Probe all discovered modules |
| `register_probe(probe)` | `None` | Add custom health probe |

### HealthReport

| Field | Type | Notes |
|-------|------|-------|
| `results` | `list[HealthResult]` | Per-module results |
| `score` | `float` | Percentage of healthy modules |
| `healthy_count` | `int` | Count by status |
| `summary()` | `str` | One-line summary string |

## Dependencies

- `system_discovery/core` for module enumeration
- `importlib` (stdlib) for import probing
- `codomyrmex.logging_monitoring`

## Constraints

- Import probing may trigger module-level side effects.
- Health score treats `degraded` as partial (0.5 weight), not full failure.

## Navigation

- [README.md](README.md) | [AGENTS.md](AGENTS.md) | [PAI.md](PAI.md)
- Parent: [system_discovery](../README.md)
