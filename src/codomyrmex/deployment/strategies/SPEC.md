# Deployment Strategies -- Technical Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

Pluggable target-based deployment strategy implementations. Each strategy receives a list of `DeploymentTarget` values, a version, and a concrete deployment function.

## Architecture

Strategy pattern with a factory over the rolling, blue-green, and canary implementations.

## Key Classes

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

## Dependencies

- **Internal**: None
- **External**: Standard library (`abc`, `time`, `threading`, `logging`, `dataclasses`, `enum`)

## Constraints

- `RollingDeployment` uses `time.sleep()` between batches, blocking the calling thread.
- `CanaryDeployment` uses `time.sleep()` between stages.
- `BlueGreenDeployment.rollback()` always returns success with `duration_ms=0`.
- `create_strategy` supports the three target-based strategies: rolling, blue-green, and canary.

## Error Handling

- `create_strategy` raises `ValueError` for unknown strategy types.
- Strategy `deploy()` methods catch `Exception` per target and accumulate errors in `DeploymentResult.errors`.

## Navigation

- **Self**: `SPEC.md`
- **Parent**: [../README.md](../README.md)
- **Readme**: [README.md](README.md)
- **Agents**: [AGENTS.md](AGENTS.md)
- **Repository Root**: [README.md](../../../../README.md)
