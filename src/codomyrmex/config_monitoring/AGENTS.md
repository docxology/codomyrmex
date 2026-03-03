# Config Monitoring -- Agent Coordination

## Purpose

Configuration change detection, drift analysis, compliance auditing, and file-system hot-reload. Monitors configuration files for modifications, takes snapshots for drift comparison, and audits configurations against compliance rules.

## Key Components

| Component | File | Role |
|-----------|------|------|
| `ConfigChange` | `config_monitor.py` | Change record: path, type (created/modified/deleted), hashes, source |
| `ConfigAudit` | `config_monitor.py` | Audit record: environment, compliance status, issues, recommendations |
| `ConfigSnapshot` | `config_monitor.py` | Snapshot for drift detection: per-file SHA-256 hashes, file count |
| `ConfigurationMonitor` | `config_monitor.py` | Change tracking, snapshot creation, drift analysis, compliance auditing |
| `ConfigWatcher` | `watcher.py` | Filesystem mtime-polling hot-reload with thread-safe daemon thread |
| `mcp_tools` | `mcp_tools.py` | Exposes configuration monitoring capabilities via MCP |

## Operating Contracts

- **Hash-based change detection**: `ConfigurationMonitor.calculate_file_hash()` uses SHA-256 to detect file modifications.
- **Persistence**: Hashes are stored in `config_monitoring/config_hashes.json`. Snapshots in `config_monitoring/snapshots/`. Audits in `config_audits/`.
- **Snapshot drift**: `detect_drift()` compares current file hashes against a saved `ConfigSnapshot` to find added, removed, and modified files.
- **Compliance auditing**: `audit_configuration()` scans for sensitive data patterns (passwords, keys), overly permissive file permissions, and policy violations.
- **Hot-reload**: `ConfigWatcher` polls `mtime` at a configurable interval (default 5 seconds) and invokes a callback on change. Thread-safe `start()`/`stop()`.

## Integration Points

- **Logging**: Uses `codomyrmex.logging_monitoring.core.logger_config.get_logger`.
- **Exceptions**: Uses `codomyrmex.exceptions.CodomyrmexError`.
- **No external deps**: Uses only standard library (`hashlib`, `json`, `re`, `pathlib`, `threading`, `time`).

## Navigation

- **Parent**: [config_management/](../config_management/AGENTS.md)
- **Specification**: [SPEC.md](SPEC.md)
- **README**: [README.md](README.md)
