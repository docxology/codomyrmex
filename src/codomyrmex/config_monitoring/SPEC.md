# Config Monitoring -- Functional Specification

## Overview

Configuration monitoring, drift detection, compliance auditing, and hot-reload. 

## Key Classes

### `ConfigChange` (`config_monitor.py`)
Record of a single file change. Includes path, type, timestamp, hashes, and source.

### `ConfigAudit` (`config_monitor.py`)
Result of a compliance audit. Includes status, issues found, and recommendations.

### `ConfigSnapshot` (`config_monitor.py`)
Point-in-time state of multiple configuration files for drift detection.

### `ConfigurationMonitor` (`config_monitor.py`)
Main service class.
- `calculate_file_hash(path)`: SHA-256 hash.
- `detect_config_changes(paths)`: Compares current files with persisted hashes.
- `create_snapshot(env, dir)`: Saves current state of a directory.
- `detect_drift(snapshot_id, dir)`: Compares directory with a saved snapshot.
- `audit_configuration(env, dir)`: Checks for security issues (permissions, secrets).

### `ConfigWatcher` (`watcher.py`)
Thread-safe filesystem poller for hot-reloading.
- `start()` / `stop()`: Lifecycle management.
- `is_alive`: Status check.

## Directory Layout
- `{workspace}/config_monitoring/config_hashes.json`: Current known hashes.
- `{workspace}/config_monitoring/snapshots/`: JSON snapshot files.
- `{workspace}/config_audits/`: JSON audit reports.

## Constraints
- **Zero-Mock**: Tests must use real filesystem.
- **Polling**: Watcher uses polling, not OS-specific events, for maximum portability.
- **Regex Audit**: Compliance checks use regex patterns for secret detection.

## Navigation
- **Specification**: This file
- **Agent coordination**: [AGENTS.md](AGENTS.md)
- **Parent**: [config_management/](../config_management/SPEC.md)
