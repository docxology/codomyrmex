# Health Checker Agentic Context

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose

Health checking and status reporting for Codomyrmex modules. Agents use the `HealthChecker` to verify module importability, dependency satisfaction, and RASP documentation completeness.

## Key Components

| Component | Type | Role |
|-----------|------|------|
| `HealthChecker` | Class | Runs health probes against discovered modules |
| `HealthResult` | Dataclass | Per-module health status (healthy, degraded, unhealthy) |
| `HealthReport` | Dataclass | Aggregate report with overall score and per-module results |
| `HealthProbe` | Protocol | Interface for custom health check implementations |

## Operating Contracts

- `HealthChecker.check(module_name)` returns a `HealthResult` for a single module.
- `HealthChecker.check_all()` returns a `HealthReport` covering every discovered module.
- A module is `healthy` if it imports successfully and all dependencies are satisfied.
- A module is `degraded` if it imports but has missing optional dependencies.
- A module is `unhealthy` if it fails to import or has missing required dependencies.
- RASP completeness (4 docs present) is reported but does not affect health status.

## Integration Points

- Depends on `system_discovery/core` for module enumeration.
- Backs the `health_check` MCP tool and `codomyrmex check` CLI command.
- Uses `logging_monitoring.get_logger` for structured logging.

## Navigation

- [README.md](README.md) | [SPEC.md](SPEC.md) | [PAI.md](PAI.md)
- Parent: [system_discovery](../README.md)
