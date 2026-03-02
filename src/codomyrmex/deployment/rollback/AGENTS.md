# Codomyrmex Agents — src/codomyrmex/deployment/rollback

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose

Deployment rollback management through versioned snapshots. Provides `RollbackManager` which maintains a chronological stack of `DeploymentSnapshot` instances and supports rolling back to any previously snapshotted version with verification.

## Key Components

| File | Class / Function | Role |
|------|-----------------|------|
| `__init__.py` | `SnapshotState` | Enum: ACTIVE, ROLLED_BACK, SUPERSEDED |
| `__init__.py` | `DeploymentSnapshot` | Dataclass: version, state, created_at, metadata; `to_dict()` serialization |
| `__init__.py` | `RollbackResult` | Dataclass: success, from_version, to_version, performed_at, message |
| `__init__.py` | `RollbackManager` | Core manager: `create_snapshot()`, `rollback_to(version)`, `list_snapshots()`, `verify_rollback()`, `current_version` property |

## Operating Contracts

- `create_snapshot()` marks any previously ACTIVE snapshot as SUPERSEDED before creating the new one.
- `rollback_to(version)` marks the target snapshot as ROLLED_BACK and all later snapshots as SUPERSEDED.
- `rollback_to(version)` raises `KeyError` if no snapshot with the given version exists.
- `verify_rollback()` returns `True` only when exactly one ROLLED_BACK snapshot exists and its version matches `current_version`.
- `list_snapshots()` returns shallow copies to prevent external mutation.
- Errors must be logged via `logging_monitoring` before re-raising.

## Integration Points

- **Depends on**: Standard library (`copy`, `dataclasses`, `datetime`, `enum`)
- **Used by**: `codomyrmex.deployment` parent module

## Navigation

- **Parent**: [deployment](../README.md)
- **Root**: [Root](../../../../README.md)
