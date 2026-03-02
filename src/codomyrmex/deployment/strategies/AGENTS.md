# Codomyrmex Agents — src/codomyrmex/deployment/strategies

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose

Pluggable deployment strategy implementations. Two complementary APIs exist: a target-based API (`__init__.py`) where strategies receive a list of `DeploymentTarget` objects and a `deploy_fn` callable, and a service-name-based API (`strategies.py`) where strategies receive a service name and version string.

## Key Components

| File | Class / Function | Role |
|------|-----------------|------|
| `__init__.py` | `DeploymentState` | Enum: PENDING, IN_PROGRESS, COMPLETED, FAILED, ROLLED_BACK, PAUSED |
| `__init__.py` | `DeploymentTarget` | Dataclass: id, name, address, healthy, version, metadata |
| `__init__.py` | `DeploymentResult` | Dataclass: success, targets_updated, targets_failed, duration_ms, state, errors, metadata; `to_dict()` |
| `__init__.py` | `DeploymentStrategy` | ABC (target-based): `deploy(targets, version, deploy_fn)`, `rollback(targets, previous_version, deploy_fn)` |
| `__init__.py` | `RollingDeployment` | Batched rolling deploy with configurable batch_size, delay_seconds, health_check callback |
| `__init__.py` | `BlueGreenDeployment` | Deploy to all targets, then switch traffic via switch_fn; rollback switches back |
| `__init__.py` | `CanaryDeployment` | Staged rollout (default stages: 10%, 25%, 50%, 100%) with success_threshold (0.95) |
| `__init__.py` | `create_strategy` | Factory: maps "rolling", "blue_green", "canary" to strategy classes |
| `strategies.py` | `DeploymentState` | Dataclass: service, version, strategy, status, started_at, traffic_percentage, metadata; `complete()`, `fail(reason)` |
| `strategies.py` | `DeploymentStrategy` | ABC (service-based): `execute(service_name, version)`, `rollback(state)` |
| `strategies.py` | `RollingStrategy` | Batch-based rolling deploy with batch_size, batch_count, pause_seconds |
| `strategies.py` | `CanaryStrategy` | Traffic-shifting with initial_percentage, step increment, max_steps |
| `strategies.py` | `BlueGreenStrategy` | Full environment swap; tracks active_slot ("blue"/"green") in metadata |
| `strategies.py` | `FeatureFlagStrategy` | Deploys code behind a feature flag; initial_rollout percentage, flag_name in metadata |

## Operating Contracts

- Target-based strategies (`__init__.py`) receive a `deploy_fn: Callable[[DeploymentTarget, str], bool]` for actual deployment.
- `RollingDeployment` inserts `delay_seconds` sleep between batches.
- `BlueGreenDeployment` only calls `switch_fn` when all targets deploy successfully.
- `CanaryDeployment` aborts and returns FAILED if stage success rate falls below `success_threshold`.
- Service-based strategies (`strategies.py`) track `traffic_percentage` progression and log each step.
- `FeatureFlagStrategy` sets traffic to `initial_rollout` immediately; rollback sets it to 0.
- `create_strategy` raises `ValueError` for unknown strategy types.
- Errors must be logged via `logging_monitoring` before re-raising.

## Integration Points

- **Depends on**: Standard library (`abc`, `time`, `threading`, `logging`, `dataclasses`, `enum`)
- **Used by**: `codomyrmex.deployment.manager` (both DeploymentOrchestrator and DeploymentManager)

## Navigation

- **Parent**: [deployment](../README.md)
- **Root**: [Root](../../../../README.md)
