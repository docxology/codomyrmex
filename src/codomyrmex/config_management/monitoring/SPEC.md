# Configuration Monitoring Specification
**Version**: v1.0.8 | **Status**: Active | **Last Updated**: March 2026

## Overview

Technical specification for the `config_management/monitoring` sub-module. Covers configuration change detection, snapshot-based drift analysis, compliance auditing, and file-watch hot-reload.

## Design Principles

- **Zero-Mock**: Tests use real files on disk, not mocked file systems.
- **Explicit Failure**: `detect_drift()` raises `CodomyrmexError` for unknown snapshot IDs. Hash store corruption logs a warning and continues as a first run.
- **SHA-256 Hashing**: All file comparisons use SHA-256 for change detection and snapshot integrity.
- **Bounded History**: In-memory change list is capped at 1,000 entries to prevent unbounded growth.

## Architecture

```
monitoring/
  config_monitor.py   # ConfigurationMonitor, ConfigChange, ConfigAudit, ConfigSnapshot
  watcher.py          # ConfigWatcher (threaded file watcher)
```

## Functional Requirements

1. **Change Detection**: `detect_config_changes(paths)` computes SHA-256 hashes for each file, compares against persisted hash store (`config_hashes.json`), and returns a list of `ConfigChange` records categorized as `created`, `modified`, or `deleted`.
2. **Snapshot Creation**: `create_snapshot(environment, paths)` saves file hashes to a JSON file in `config_monitoring/snapshots/` and returns a `ConfigSnapshot` with a unique ID.
3. **Drift Detection**: `detect_drift(snapshot_id, current_paths)` compares current file hashes against a saved snapshot and reports `files_in_drift`, `files_missing`, `files_added`, and per-file details.
4. **Compliance Auditing**: `audit_configuration(environment, paths)` checks file permissions (world-readable flag), scans for sensitive data patterns (password, api_key, secret, token), verifies required sections, and produces a `ConfigAudit` with compliance status.
5. **File Watching**: `ConfigWatcher` runs a daemon thread that polls file mtime at a configurable interval and invokes a callback on change.
6. **History Queries**: `get_recent_changes(hours)` filters in-memory changes by time window. `get_audit_history(environment)` returns sorted audit records.

## Interface Contracts

```python
class ConfigurationMonitor:
    def __init__(self, workspace_dir: str | None = None) -> None: ...
    def calculate_file_hash(self, file_path: str) -> str: ...
    def detect_config_changes(self, config_paths: list[str]) -> list[ConfigChange]: ...
    def create_snapshot(self, environment: str, config_paths: list[str]) -> ConfigSnapshot: ...
    def detect_drift(self, snapshot_id: str, current_paths: list[str]) -> dict[str, Any]: ...
    def audit_configuration(self, environment: str, config_paths: list[str], compliance_rules: dict[str, Any] | None = None) -> ConfigAudit: ...
    def get_recent_changes(self, hours: int = 24) -> list[ConfigChange]: ...
    def get_audit_history(self, environment: str | None = None) -> list[ConfigAudit]: ...
    def get_monitoring_summary(self) -> dict[str, Any]: ...

class ConfigWatcher:
    def __init__(self, file_path: str, callback: Callable[[], None], interval: int = 5) -> None: ...
    def start(self) -> None: ...
    def stop(self) -> None: ...
```

## Data Models

```python
@dataclass
class ConfigChange:
    change_id: str
    config_path: str
    change_type: str         # "created" | "modified" | "deleted"
    timestamp: datetime
    previous_hash: str | None
    current_hash: str | None
    changes: dict[str, Any]
    source: str              # Default: "unknown"

@dataclass
class ConfigAudit:
    audit_id: str
    timestamp: datetime
    environment: str
    compliance_status: str   # "compliant" | "non_compliant"
    issues_found: list[str]
    recommendations: list[str]
    audit_scope: dict[str, Any]

@dataclass
class ConfigSnapshot:
    snapshot_id: str
    timestamp: datetime
    environment: str
    config_hashes: dict[str, str]
    total_files: int
```

## Dependencies

- `hashlib` -- SHA-256 file hashing
- `codomyrmex.exceptions.CodomyrmexError` -- raised for missing snapshots
- `codomyrmex.logging_monitoring.core.logger_config` -- structured logging

## Constraints

- In-memory change history is capped at 1,000 entries (oldest are dropped).
- `ConfigWatcher` runs as a daemon thread; it will not prevent process exit.
- Snapshot and audit JSON files are stored in workspace subdirectories (`config_monitoring/`, `config_audits/`).

## Navigation

- [README.md](README.md) | [AGENTS.md](AGENTS.md) | [Parent](../README.md)
