# Deployment Strategies -- Technical Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

Pluggable deployment strategy implementations. Two complementary strategy ABCs exist: a target-based API (strategies receive `DeploymentTarget` lists and a `deploy_fn`) and a service-name-based API (strategies receive service name and version).

## Architecture

Strategy pattern with factory. Two parallel hierarchies share the same design but differ in interface: target-based strategies (`__init__.py`) are used by `DeploymentOrchestrator`, while service-name-based strategies (`strategies.py`) are used by `DeploymentManager`.

## Key Classes -- Target-Based API (`__init__.py`)

### `DeploymentStrategy` (ABC)

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `deploy` | `targets, version, deploy_fn` | `DeploymentResult` | Deploy version to targets using the provided function |
| `rollback` | `targets, previous_version, deploy_fn` | `DeploymentResult` | Rollback targets to previous version |

### `RollingDeployment`

Constructor: `(batch_size: int = 1, delay_seconds: float = 5.0, health_check: Callable | None = None)`

Deploys in batches with configurable delay between them. Runs optional health check per target after deploy. Rollback re-deploys the previous version using the same rolling mechanism.

### `BlueGreenDeployment`

Constructor: `(switch_fn: Callable[[str], bool] | None = None, health_check: Callable | None = None)`

Deploys to all targets first. If all succeed, calls `switch_fn(version)` to switch traffic. Rollback calls `switch_fn(previous_version)` to revert traffic.

### `CanaryDeployment`

Constructor: `(stages: list[float] = [10, 25, 50, 100], stage_duration_seconds: float = 60.0, health_check: Callable | None = None, success_threshold: float = 0.95)`

Deploys in percentage stages. Sleeps `stage_duration_seconds` between stages. Aborts if success rate drops below `success_threshold`. Rollback uses `RollingDeployment(batch_size=5)`.

### `create_strategy` (Factory)

`create_strategy(strategy_type: str, **kwargs) -> DeploymentStrategy`

Maps: `"rolling"` -> `RollingDeployment`, `"blue_green"` -> `BlueGreenDeployment`, `"canary"` -> `CanaryDeployment`. Raises `ValueError` for unknown types.

## Key Classes -- Service-Based API (`strategies.py`)

### `DeploymentState` (Dataclass)

| Field | Type | Description |
|-------|------|-------------|
| `service` | `str` | Service name |
| `version` | `str` | Target version |
| `strategy` | `str` | Strategy name |
| `status` | `str` | "pending", "in_progress", "completed", "rolled_back", "failed" |
| `traffic_percentage` | `float` | Current traffic percentage (0.0 to 100.0) |

Methods: `complete()` (sets status to "completed", traffic to 100%), `fail(reason)` (sets status to "failed", stores reason)

### `DeploymentStrategy` (ABC)

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `execute` | `service_name, version` | `DeploymentState` | Execute deployment |
| `rollback` | `state: DeploymentState` | `DeploymentState` | Roll back deployment |

### `RollingStrategy`

Constructor: `(batch_size: int = 1, batch_count: int = 4, pause_seconds: float = 0.0)`

### `CanaryStrategy`

Constructor: `(initial_percentage: int = 10, step: int = 20, max_steps: int = 5)`

### `BlueGreenStrategy`

Tracks `active_slot` ("blue"/"green") in metadata. Rollback swaps back to "blue".

### `FeatureFlagStrategy`

Constructor: `(flag_name: str = "", initial_rollout: float = 0.0)`

Auto-generates flag name as `ff_{service}_{version}` if not provided. Rollback sets traffic to 0%.

## Dependencies

- **Internal**: None
- **External**: Standard library (`abc`, `time`, `threading`, `logging`, `dataclasses`, `enum`)

## Constraints

- `RollingDeployment` uses `time.sleep()` between batches, blocking the calling thread.
- `CanaryDeployment` uses `time.sleep()` between stages.
- `BlueGreenDeployment.rollback()` always returns success with `duration_ms=0`.
- `create_strategy` only supports the three target-based strategies; service-based strategies must be instantiated directly.

## Error Handling

- `create_strategy` raises `ValueError` for unknown strategy types.
- Target-based strategy `deploy()` methods catch `Exception` per target and accumulate errors in `DeploymentResult.errors`.
- Service-based strategies do not catch exceptions internally; callers (e.g., `DeploymentManager`) handle them.
