# Codomyrmex Agents — src/codomyrmex/deployment/manager

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose

Deployment orchestration layer. Contains two complementary classes: `DeploymentOrchestrator` (plan-execute-verify lifecycle using target-based strategies and health checks) and `DeploymentManager` (simpler deploy-and-rollback with history tracking using service-name-based strategies).

## Key Components

| File | Class / Function | Role |
|------|-----------------|------|
| `__init__.py` | `PlanState` | Enum: DRAFT, APPROVED, EXECUTING, COMPLETED, FAILED |
| `__init__.py` | `DeploymentPlan` | Dataclass: version, targets, strategy, state, created_at, metadata |
| `__init__.py` | `DeploymentStatus` | Dataclass: active_plan, last_result, last_health, deployments_completed, deployments_failed |
| `__init__.py` | `DeploymentOrchestrator` | Full lifecycle: `plan_deployment()`, `execute_deployment()`, `verify_deployment()`, `get_deployment_status()` |
| `manager.py` | `DeploymentManager` | Simpler API: `deploy(service, version, strategy)`, `rollback(service, strategy)`, `get_active()`, `history`, `active_deployments`, `summary()` |

## Operating Contracts

- `DeploymentOrchestrator` requires a `DeploymentStrategy` (from `deployment.strategies`) and optionally a `HealthChecker` (from `deployment.health_checks`) and a `deploy_fn` callable.
- `execute_deployment()` raises `RuntimeError` if the plan is not in DRAFT or APPROVED state.
- `verify_deployment()` returns `HealthStatus.HEALTHY` optimistically if no `HealthChecker` was provided.
- `DeploymentManager.deploy()` catches exceptions from strategy execution and records a failed `DeploymentState`.
- `DeploymentManager.rollback()` returns `None` if no active deployment exists for the given service.
- Errors must be logged via `logging_monitoring` before re-raising.

## Integration Points

- **Depends on**: `codomyrmex.deployment.health_checks` (HealthChecker, HealthStatus), `codomyrmex.deployment.strategies` (DeploymentStrategy, DeploymentTarget, DeploymentResult, DeploymentState)
- **Used by**: `codomyrmex.deployment` parent module

## Navigation

- **Parent**: [deployment](../README.md)
- **Root**: [Root](../../../../README.md)
