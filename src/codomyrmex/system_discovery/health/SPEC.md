# Health Checker -- Technical Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

Module health verification for Codomyrmex packages. `HealthChecker` imports a
top-level `codomyrmex.<module>` package and then runs a check that exercises
it (renders a plot, runs the static analyzer on a sample file, executes code
in the sandbox, pings Docker, ...). `HealthReporter` aggregates the results.

## Architecture

```text
HealthChecker()
  +-- module_checks: dict[str, Callable]   # top-level package -> dedicated check
  +-- perform_health_check(module_name) -> HealthCheckResult
  +-- run_checks(module_names=None) -> dict[str, HealthCheckResult]

HealthCheckResult
  +-- module_name, status: HealthStatus, timestamp
  +-- checks_performed, issues, recommendations: list[str]
  +-- metrics: dict, dependencies: dict[str, HealthStatus]
  +-- to_dict() -> dict

HealthReporter()
  +-- generate_health_report(modules) -> HealthReport
```

## Key Classes

### HealthChecker Methods

| Method | Returns | Description |
| --- | --- | --- |
| `perform_health_check(module_name)` | `HealthCheckResult` | Import the package, then run its dedicated check from `module_checks`, or a generic import-and-inspect check |
| `run_checks(module_names=None)` | `dict[str, HealthCheckResult]` | Check several modules; defaults to every module in `module_checks` |

Dedicated checks exist for `logging_monitoring`, `environment_setup`,
`static_analysis`, `coding`, `data_visualization`, `git_operations`,
`security`, `llm`, `performance`, `logistics` and `containerization`.

### HealthStatus

`healthy` (no issues), `degraded` (issues that do not mention an import,
dependency or unavailability), `unhealthy` (the package does not import, or
such a critical issue) and `unknown` (the check itself raised).

## Consumers

- `codomyrmex.system_discovery.mcp_tools.health_check` — MCP tool; checks one
  module or every module in `module_checks`.
- `cli_commands()["health"]` in `system_discovery/__init__.py` — prints each
  checked module's status and issues.

## Dependencies

- `importlib` (stdlib) for import probing
- `codomyrmex.logging_monitoring`
- The modules each dedicated check exercises; `docker` (optional) for the
  containerization check

## Constraints

- Import probing may trigger module-level side effects.
- The `coding` and `containerization` checks need a running Docker daemon;
  without one they report `degraded` with the reason.
- Health score treats `degraded` as partial (0.5 weight), not full failure.

## Navigation

- [README.md](README.md) | [AGENTS.md](AGENTS.md) | [PAI.md](PAI.md)
- Parent: [system_discovery](../README.md)
