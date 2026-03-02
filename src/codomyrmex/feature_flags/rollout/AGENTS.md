# Codomyrmex Agents — src/codomyrmex/feature_flags/rollout

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose

Staged gradual rollout management for feature flags. Provides `RolloutManager` to create, advance, pause, and inspect multi-stage rollouts with a defined lifecycle (`PENDING -> ACTIVE -> PAUSED -> COMPLETED / ABORTED`). Each rollout is configured with an ordered list of percentage stages (e.g., 5%, 25%, 50%, 100%) and a minimum delay between advances.

## Key Components

| File | Class / Function | Role |
|------|-----------------|------|
| `__init__.py` | `RolloutState` | Enum with five lifecycle states: PENDING, ACTIVE, PAUSED, COMPLETED, ABORTED |
| `__init__.py` | `RolloutConfig` | Dataclass holding `stages` (list of percentages) and `stage_delay_seconds`; validates on init |
| `__init__.py` | `RolloutStatus` | Dataclass snapshot: flag_name, state, current stage index, current percentage, timestamps, metadata |
| `__init__.py` | `RolloutManager` | Manages per-flag rollout entries: create, advance through stages, pause, and query status |
| `__init__.py` | `_RolloutEntry` | Internal mutable dataclass storing a rollout's config, state, index, and timestamps |

## Operating Contracts

- `RolloutConfig.stages` must contain at least one value; each stage must be in (0, 100].
- `create_rollout` replaces any existing rollout for the same flag name.
- `advance_rollout` moves to the next stage index; sets state to COMPLETED when all stages are exhausted.
- `advance_rollout` and `pause_rollout` raise `RuntimeError` if the rollout is not in an advanceable or active state respectively.
- `_get_entry` raises `KeyError` for unknown flag names.
- Errors must be logged via `logging_monitoring` before re-raising.

## Integration Points

- **Depends on**: `datetime`, `enum`, `dataclasses` (standard library only)
- **Used by**: `feature_flags.core.FeatureManager` (to control staged percentage increases over time)

## Navigation

- **Parent**: [feature_flags](../README.md)
- **Root**: [Root](../../../../README.md)
