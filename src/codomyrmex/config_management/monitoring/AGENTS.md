# Config Management Monitoring -- Agent Coordination

## Purpose

Configuration change detection, drift analysis, compliance auditing, and file-system hot-reload. Monitors configuration files for modifications, takes snapshots for drift comparison, and audits configurations against compliance rules.

## Key Components

| Component | File | Role |
|-----------|------|------|
| `ConfigChange` | `config_monitor.py` | Change record: path, type (created/modified/deleted), hashes, source |
| `ConfigAudit` | `config_monitor.py` | Audit record: environment, compliance status, issues, recommendations |
| `ConfigSnapshot` | `config_monitor.py` | Snapshot for drift detection: per-file SHA-256 hashes, file count |
| `ConfigurationMonitor` | `config_monitor.py` | Change tracking, snapshot creation, drift analysis, compliance auditing |
| `ConfigWatcher` | `watcher.py` | Filesystem mtime-polling hot-reload with daemon thread |

## Operating Contracts

- **Hash-based change detection**: `ConfigurationMonitor.calculate_file_hash()` uses SHA-256 to detect file modifications.
- **Snapshot drift**: `detect_drift()` compares current file hashes against a saved `ConfigSnapshot` to find added, removed, and modified files.
- **Compliance auditing**: `audit_configuration()` scans for sensitive data patterns (regex-based), missing required files, and policy violations.
- **Directory structure**: Monitoring data is stored under `{workspace}/config_monitoring/snapshots/`; audit records under `{workspace}/config_audits/`.
- **Hot-reload**: `ConfigWatcher` polls `os.path.getmtime()` at a configurable interval (default 5 seconds) on a daemon thread and invokes a callback on change.
- **No MCP tools**: This submodule does not directly expose MCP tools. The parent `config_management` module handles MCP exposure.

## Integration Points

- **Logging**: `ConfigurationMonitor` uses `codomyrmex.logging_monitoring.core.logger_config.get_logger`; `ConfigWatcher` uses standard `logging`.
- **Exceptions**: `ConfigurationMonitor` imports `codomyrmex.exceptions.CodomyrmexError`.
- **No external deps**: Uses only standard library (`hashlib`, `json`, `re`, `pathlib`, `threading`, `time`).

## Navigation

- **Parent**: [config_management/](../AGENTS.md)
- **Siblings**: [core/](../core/AGENTS.md)
- **Specification**: [SPEC.md](SPEC.md)
