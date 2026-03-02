# Config Management Monitoring -- Functional Specification

## Overview

Configuration monitoring, drift detection, compliance auditing, and hot-reload. Two files: `config_monitor.py` (monitoring system) and `watcher.py` (filesystem watcher).

## Key Classes

### `ConfigChange` (`config_monitor.py`)

| Field | Type | Description |
|-------|------|-------------|
| `change_id` | `str` | Unique change identifier |
| `config_path` | `str` | Path to changed config file |
| `change_type` | `str` | `"created"`, `"modified"`, or `"deleted"` |
| `timestamp` | `datetime` | When the change occurred |
| `previous_hash` | `str \| None` | SHA-256 hash before change |
| `current_hash` | `str \| None` | SHA-256 hash after change |
| `changes` | `dict[str, Any]` | Detailed change information |
| `source` | `str` | Who made the change (default `"unknown"`) |

### `ConfigAudit` (`config_monitor.py`)

| Field | Type | Description |
|-------|------|-------------|
| `audit_id` | `str` | Unique audit identifier |
| `timestamp` | `datetime` | Audit execution time |
| `environment` | `str` | Target environment |
| `compliance_status` | `str` | Overall compliance result |
| `issues_found` | `list[str]` | List of compliance issues |
| `recommendations` | `list[str]` | Suggested remediations |
| `audit_scope` | `dict[str, Any]` | Scope parameters |

### `ConfigSnapshot` (`config_monitor.py`)

| Field | Type | Description |
|-------|------|-------------|
| `snapshot_id` | `str` | Unique snapshot identifier |
| `timestamp` | `datetime` | Snapshot creation time |
| `environment` | `str` | Environment name |
| `config_hashes` | `dict[str, str]` | File path to SHA-256 hash mapping |
| `total_files` | `int` | Number of files in snapshot |

### `ConfigurationMonitor` (`config_monitor.py`)

| Method | Description |
|--------|-------------|
| `calculate_file_hash(file_path) -> str` | SHA-256 hash of file contents |
| `record_change(config_path, change_type, ...)` | Create and store a `ConfigChange` |
| `create_snapshot(environment, config_dir)` | Hash all files in directory; store `ConfigSnapshot` |
| `detect_drift(snapshot_id, config_dir)` | Compare current hashes to snapshot; return added/removed/modified |
| `audit_configuration(environment, config_dir)` | Compliance check: sensitive data regex scan, required file check |
| `get_changes(config_path=None)` | Retrieve change history, optionally filtered by path |

Directory layout:
- `{workspace}/config_monitoring/` -- monitoring data root
- `{workspace}/config_monitoring/snapshots/` -- snapshot files
- `{workspace}/config_audits/` -- audit records

### `ConfigWatcher` (`watcher.py`)

Filesystem hot-reload watcher using `os.path.getmtime()` polling.

| Field | Type | Description |
|-------|------|-------------|
| `file_path` | `str` | Path to watched config file |
| `callback` | `Callable[[], None]` | Function invoked on change |
| `interval` | `int` | Poll interval in seconds (default 5) |

| Method | Description |
|--------|-------------|
| `start()` | Launch daemon thread for polling |
| `stop()` | Signal thread to stop; join with 5s timeout |

Thread is set as daemon (`daemon=True`) so it does not prevent process exit.

## Dependencies

- `codomyrmex.logging_monitoring.core.logger_config` -- structured logging (monitor)
- `codomyrmex.exceptions.CodomyrmexError` -- base exception (monitor)
- Standard library: `hashlib`, `json`, `re`, `pathlib`, `threading`, `time`, `os`, `logging`

## Constraints

- Drift detection requires a previously saved snapshot; raises on unknown `snapshot_id`.
- `ConfigWatcher` uses mtime polling, not filesystem events (no `inotify`/`FSEvents` dependency).
- Compliance auditing uses hardcoded regex patterns for sensitive data detection (passwords, tokens, keys).

## Navigation

- **Specification**: This file
- **Agent coordination**: [AGENTS.md](AGENTS.md)
- **Parent**: [config_management/](../SPEC.md)
