# Codomyrmex Agents — src/codomyrmex/deployment/gitops

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose

GitOps synchronization between a Git repository and deployed state. Detects drift between the desired revision (branch HEAD) and the actual deployed revision, and reconciles differences by updating internal tracking state.

## Key Components

| File | Class / Function | Role |
|------|-----------------|------|
| `__init__.py` | `SyncState` | Enum: IN_SYNC, DRIFTED, UNKNOWN, SYNCING, ERROR |
| `__init__.py` | `SyncStatus` | Dataclass: state, desired_revision, actual_revision, last_synced_at, drift_details; `to_dict()` serialization |
| `__init__.py` | `GitOpsSynchronizer` | Core synchronizer: `sync_state()`, `detect_drift()`, `reconcile()`, `get_sync_status()`; tracks repo_path and target_branch |
| `gitops.py` | `GitOpsSynchronizer` | Alternate implementation: `sync(branch)` clones or hard-resets repo; `get_version()` returns current commit SHA |

## Operating Contracts

- `GitOpsSynchronizer` (in `__init__.py`) resolves HEAD via `git rev-parse` with a 10-second subprocess timeout.
- `detect_drift()` returns `True` when desired and actual revisions differ.
- `reconcile()` updates `_actual_revision` to match desired and sets state to `IN_SYNC`.
- `gitops.py` variant uses `git clone` for first sync and `git reset --hard origin/{branch}` for updates.
- Errors must be logged via `logging_monitoring` before re-raising.

## Integration Points

- **Depends on**: Standard library (`subprocess`, `hashlib`, `logging`, `dataclasses`, `enum`, `os`)
- **Used by**: `codomyrmex.deployment` parent module

## Navigation

- **Parent**: [deployment](../README.md)
- **Root**: [Root](../../../../README.md)
