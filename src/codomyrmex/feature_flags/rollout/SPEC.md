# Gradual Rollout -- Technical Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

Provides staged rollout management for feature flags. A rollout walks through an ordered list of percentage stages, allowing operators to advance, pause, or inspect rollout progress. The module is in-memory and stateless across restarts -- persistence is delegated to the caller or the `storage` submodule.

## Architecture

`RolloutManager` holds a `dict[str, _RolloutEntry]` mapping flag names to their rollout state. Each entry wraps a `RolloutConfig` (the stage plan) and mutable state (current index, lifecycle state, timestamps). State transitions follow the `RolloutState` enum lifecycle.

## Key Classes

### `RolloutState` (Enum)

| Value | Description |
|-------|-------------|
| `PENDING` | Rollout created but not yet started |
| `ACTIVE` | Rollout is live at the current stage percentage |
| `PAUSED` | Rollout is temporarily frozen |
| `COMPLETED` | All stages have been exhausted |
| `ABORTED` | Rollout was cancelled before completion |

### `RolloutConfig`

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `stages` | `list[float]` | `[5.0, 25.0, 50.0, 100.0]` | Ordered rollout percentages |
| `stage_delay_seconds` | `float` | `3600.0` | Minimum seconds between automatic advances |

Validation in `__post_init__`: raises `ValueError` if stages is empty or any value is outside (0, 100].

### `RolloutStatus`

| Field | Type | Description |
|-------|------|-------------|
| `flag_name` | `str` | The feature flag this rollout controls |
| `state` | `RolloutState` | Current lifecycle state |
| `current_stage_index` | `int` | Index into the config stages list |
| `current_percentage` | `float` | The active rollout percentage |
| `started_at` | `datetime` | When the rollout was created |
| `updated_at` | `datetime` | When the rollout was last modified |
| `metadata` | `dict[str, Any]` | Arbitrary extra data |

### `RolloutManager`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `create_rollout` | `flag_name: str, config: RolloutConfig` | `RolloutStatus` | Create (or replace) a rollout starting at stage 0 in ACTIVE state |
| `advance_rollout` | `flag_name: str` | `RolloutStatus` | Move to next stage; COMPLETED when past last stage |
| `get_rollout_status` | `flag_name: str` | `RolloutStatus` | Return current status snapshot |
| `pause_rollout` | `flag_name: str` | `RolloutStatus` | Pause an ACTIVE rollout (sets state to PAUSED) |

## Dependencies

- **Internal**: None
- **External**: Standard library only (`datetime`, `enum`, `dataclasses`)

## Constraints

- In-memory only: rollout state does not survive process restarts.
- `advance_rollout` raises `RuntimeError` if state is not ACTIVE or PAUSED.
- `pause_rollout` raises `RuntimeError` if state is not ACTIVE.
- All status queries raise `KeyError` for unknown flag names.
- Zero-mock: real data only, `NotImplementedError` for unimplemented paths.

## Error Handling

- `KeyError` raised when querying or advancing a flag with no registered rollout.
- `RuntimeError` raised on invalid state transitions (e.g., advancing a COMPLETED rollout).
- `ValueError` raised by `RolloutConfig.__post_init__` for invalid stage values.
- All errors logged before propagation.
