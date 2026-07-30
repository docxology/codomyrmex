# Deployment Manager -- Technical Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

Deployment management with target-based execution, history tracking, and rollback.

## Architecture

`DeploymentManager` delegates to `DeploymentStrategy.deploy(targets, version, deploy_fn)` and `DeploymentStrategy.rollback(targets, previous_version, deploy_fn)`, then records results and active versions.

## Key Classes

### `DeploymentManager`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `deploy` | `service_name, version, strategy, targets` | `DeploymentResult` | Executes deployment; appends the result to history; tracks the active version |
| `rollback` | `service_name, previous_version, strategy, targets` | `DeploymentResult` | Rolls back targets and records the result |
| `get_active_version` | `service_name` | `str \ | None` | Returns the current active version for a service |
| `summary` | -- | `dict` | Returns counts: total_deployments, active_services, completed, failed, rolled_back |

Property: `history` (copy of the recorded `DeploymentResult` list)

## Dependencies

- **Internal**: `deployment.health_checks` (HealthChecker, HealthStatus), `deployment.strategies` (DeploymentStrategy, DeploymentTarget, DeploymentResult, DeploymentState)
- **External**: Standard library (`logging`, `dataclasses`, `enum`, `datetime`)

## Constraints

- `_default_deploy` is a no-op that always succeeds (sets target version and returns True).
- `DeploymentManager.deploy()` catches strategy exceptions and returns a failed result.

## Error Handling

- `DeploymentManager.deploy` catches all exceptions, creates a failed `DeploymentResult`, and logs the error.

## Navigation

- **Self**: `SPEC.md`
- **Parent**: [../README.md](../README.md)
- **Readme**: [README.md](README.md)
- **Agents**: [AGENTS.md](AGENTS.md)
- **Repository Root**: [README.md](../../../../README.md)
