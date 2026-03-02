# Codomyrmex Agents — src/codomyrmex/feature_flags/core

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose

Central feature flag evaluation engine. Provides `FeatureManager`, the primary entry point for creating, evaluating, persisting, and overriding feature flags. Supports boolean on/off flags, percentage-based rollouts with deterministic user hashing, allowlist/denylist targeting, time-window activation, and multivariate values via metadata.

## Key Components

| File | Class / Function | Role |
|------|-----------------|------|
| `manager.py` | `FlagDefinition` | Dataclass defining a flag: key, enabled state, percentage, allow/deny lists, time window, description, metadata |
| `manager.py` | `FeatureManager` | Evaluation engine with prioritized resolution: override > denylist > allowlist > time window > percentage > boolean |
| `manager.py` | `FeatureManager.is_enabled` | Evaluates a flag for a given context (user_id, group, etc.) following the six-step priority chain |
| `manager.py` | `FeatureManager.get_value` | Retrieves multivariate flag values from `metadata["value"]` |
| `manager.py` | `FeatureManager.load_from_file` / `save_to_file` | JSON file persistence for flag definitions |
| `manager.py` | `FeatureManager.set_override` / `clear_override` | In-memory test override stack (highest evaluation priority) |

## Operating Contracts

- Flag evaluation follows a strict six-step priority: test overrides, denylist, allowlist, time window, percentage rollout, boolean default.
- Percentage rollout uses `hash(f"{key}:{user_id}") % 100` for deterministic, sticky assignment without external state.
- If a flag key does not exist, `is_enabled` returns the caller-supplied `default` (defaults to `False`).
- `load_from_file` accepts both `bool` values and `dict` definitions in the JSON payload.
- Errors must be logged via `logging_monitoring` before re-raising.

## Integration Points

- **Depends on**: `json`, `pathlib.Path`, `time` (standard library only)
- **Used by**: `feature_flags.strategies`, `feature_flags.rollout`, any module needing runtime flag checks

## Navigation

- **Parent**: [feature_flags](../README.md)
- **Root**: [Root](../../../../README.md)
