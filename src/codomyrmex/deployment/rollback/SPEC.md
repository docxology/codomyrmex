# Rollback Management -- Technical Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

Snapshot-based deployment rollback. `RollbackManager` maintains a chronological stack of `DeploymentSnapshot` instances and supports targeted rollback to any previously captured version, with state verification.

## Architecture

Stack-based design: snapshots are appended chronologically. Creating a new snapshot supersedes the previous active one. Rolling back marks the target as ROLLED_BACK and later entries as SUPERSEDED, then updates the current version pointer.

## Key Classes

### `DeploymentSnapshot`

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `version` | `str` | -- | Version string captured in this snapshot |
| `state` | `SnapshotState` | `ACTIVE` | ACTIVE, ROLLED_BACK, or SUPERSEDED |
| `created_at` | `datetime` | `datetime.now()` | When the snapshot was taken |
| `metadata` | `dict[str, Any]` | `{}` | Arbitrary metadata (config hash, target count, etc.) |

Method: `to_dict() -> dict`

### `RollbackResult`

| Field | Type | Description |
|-------|------|-------------|
| `success` | `bool` | Whether the rollback completed without errors |
| `from_version` | `str` | Version before the rollback |
| `to_version` | `str` | Version that was restored |
| `performed_at` | `datetime` | When the rollback was executed |
| `message` | `str` | Human-readable summary |

### `RollbackManager`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `create_snapshot` | `version, metadata` | `DeploymentSnapshot` | Creates snapshot; supersedes previous active |
| `rollback_to` | `version: str` | `RollbackResult` | Restores to target version; marks later snapshots SUPERSEDED |
| `list_snapshots` | -- | `list[DeploymentSnapshot]` | Returns shallow copies in chronological order |
| `verify_rollback` | -- | `bool` | True if exactly one ROLLED_BACK snapshot matches current_version |
| `current_version` | -- (property) | `str \| None` | Currently active version |

## Dependencies

- **Internal**: None
- **External**: Standard library (`copy`, `dataclasses`, `datetime`, `enum`)

## Constraints

- Snapshots are stored in memory only; no persistence layer.
- `rollback_to` raises `KeyError` if no snapshot matches the requested version.
- `verify_rollback` expects exactly one snapshot in ROLLED_BACK state for consistency.
- `list_snapshots` returns `copy.copy()` of each snapshot to prevent mutation of internal state.

## Error Handling

- `rollback_to` raises `KeyError` for unknown versions.
- No other exceptions are raised; operations are purely in-memory.
