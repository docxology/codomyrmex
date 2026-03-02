# Deployment Manager -- Technical Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

Deployment orchestration and management. Two classes serve different use cases: `DeploymentOrchestrator` provides a plan-execute-verify lifecycle with health check integration, while `DeploymentManager` provides a simpler deploy/rollback interface with history tracking.

## Architecture

`DeploymentOrchestrator` follows a plan-execute-verify pipeline using target-based strategies (`DeploymentStrategy.deploy(targets, version, deploy_fn)`). `DeploymentManager` uses service-name-based strategies (`DeploymentStrategy.execute(service_name, version)`) and maintains a history list and active-deployment map.

## Key Classes

### `DeploymentOrchestrator`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `plan_deployment` | `version, targets, strategy, metadata` | `DeploymentPlan` | Creates plan in DRAFT state |
| `execute_deployment` | `plan: DeploymentPlan` | `DeploymentResult` | Executes plan; transitions state through EXECUTING to COMPLETED/FAILED |
| `verify_deployment` | -- | `HealthStatus` | Runs health checks; returns HEALTHY if no checker configured |
| `get_deployment_status` | -- | `DeploymentStatus` | Returns current status snapshot |

Constructor: `(health_checker: HealthChecker | None, deploy_fn: Callable | None)`

### `DeploymentManager`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `deploy` | `service_name, version, strategy` | `DeploymentState` | Executes deployment; appends to history; tracks active deployment |
| `rollback` | `service_name, strategy` | `DeploymentState \| None` | Rolls back active deployment; returns None if no active deployment |
| `get_active` | `service_name` | `DeploymentState \| None` | Returns current active deployment for a service |
| `summary` | -- | `dict` | Returns counts: total_deployments, active_services, completed, failed, rolled_back |

Properties: `history` (list of all DeploymentState), `active_deployments` (dict of service name to DeploymentState)

## Dependencies

- **Internal**: `deployment.health_checks` (HealthChecker, HealthStatus), `deployment.strategies` (DeploymentStrategy, DeploymentTarget, DeploymentResult, DeploymentState)
- **External**: Standard library (`logging`, `dataclasses`, `enum`, `datetime`)

## Constraints

- `execute_deployment` raises `RuntimeError` for plans not in DRAFT or APPROVED state.
- `_default_deploy` is a no-op that always succeeds (sets target version and returns True).
- `DeploymentManager.deploy()` catches all exceptions from strategy execution and returns a failed state.
- `DeploymentManager.rollback()` removes the service from `_active` after rollback.

## Error Handling

- `DeploymentOrchestrator.execute_deployment` raises `RuntimeError` for invalid plan states.
- `DeploymentManager.deploy` catches all exceptions, creates a failed `DeploymentState`, and logs the error.
- `DeploymentManager.rollback` logs a warning and returns `None` when no active deployment exists.
