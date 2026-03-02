# GitOps -- Technical Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

Git-based deployment synchronization. Provides `GitOpsSynchronizer` to track desired vs. actual deployment revisions, detect drift, and reconcile by updating internal state. Two implementations exist: a drift-detection model (`__init__.py`) and a clone/pull model (`gitops.py`).

## Architecture

Single-class design per file. `__init__.py` exposes the drift-detection synchronizer that compares `git rev-parse` output against an internally tracked actual revision. `gitops.py` exposes a simpler clone-or-pull synchronizer for keeping a local checkout current.

## Key Classes

### `GitOpsSynchronizer` (`__init__.py`)

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `sync_state` | -- | `SyncStatus` | Fetches HEAD of target branch, compares with actual revision |
| `detect_drift` | -- | `bool` | Returns True if desired and actual revisions differ |
| `reconcile` | -- | `SyncStatus` | Updates actual revision to match desired; sets state to IN_SYNC |
| `get_sync_status` | -- | `SyncStatus` | Returns last known status without re-fetching |

Constructor: `(repo_path: str, target_branch: str = "main")`

### `SyncStatus`

| Field | Type | Description |
|-------|------|-------------|
| `state` | `SyncState` | IN_SYNC, DRIFTED, UNKNOWN, SYNCING, or ERROR |
| `desired_revision` | `str \| None` | Git revision representing desired state |
| `actual_revision` | `str \| None` | Currently deployed revision |
| `last_synced_at` | `datetime \| None` | Timestamp of last successful sync |
| `drift_details` | `list[str]` | Description of detected differences |

### `GitOpsSynchronizer` (`gitops.py`)

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `sync` | `branch: str = "main"` | `bool` | Clones repo if absent, hard-resets if present |
| `get_version` | -- | `str \| None` | Returns current commit SHA of local repo |

Constructor: `(repo_url: str, local_path: str)`

## Dependencies

- **Internal**: None
- **External**: Standard library (`subprocess`, `os`, `hashlib`, `logging`)

## Constraints

- `_get_head_revision` uses `subprocess.run` with a 10-second timeout; returns `None` on failure.
- `reconcile()` does not perform an actual deployment; it updates internal tracking state only.
- `gitops.py` `sync()` uses `git reset --hard`, which discards local changes.

## Error Handling

- `_get_head_revision` catches `SubprocessError` and `FileNotFoundError`, logs warning, returns `None`.
- `sync()` catches `CalledProcessError`, logs error, returns `False`.
- `get_version()` catches all exceptions, logs warning, returns `None`.
