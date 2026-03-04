# Configuration Monitoring
**Version**: v1.1.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

Configuration monitoring and auditing sub-module for `config_management`. Provides change detection via SHA-256 hash comparison, configuration drift analysis against saved snapshots, compliance auditing (permission checks, sensitive data detection), and hot-reload file watching via a background thread.

## PAI Integration

| Algorithm Phase | Role |
|----------------|------|
| OBSERVE | Detect configuration file changes, take snapshots, monitor drift |
| VERIFY | Audit configurations for compliance (permissions, secrets, required sections) |

## Key Exports

| Export | Type | Description |
|--------|------|-------------|
| `ConfigurationMonitor` | Class | Core monitor: change detection, snapshots, drift analysis, auditing |
| `ConfigWatcher` | Class | Threaded file watcher that triggers a callback on file modification |
| `ConfigChange` | Dataclass | Record of a configuration change (created/modified/deleted) |
| `ConfigAudit` | Dataclass | Audit result with compliance status, issues, and recommendations |
| `ConfigSnapshot` | Dataclass | Point-in-time snapshot of configuration file hashes for drift detection |
| `monitor_config_changes` | Function | Convenience function to run an initial change detection scan |

## Quick Start

```python
from codomyrmex.config_management.monitoring.config_monitor import (
    ConfigurationMonitor,
    ConfigSnapshot,
)

# Initialize monitor
monitor = ConfigurationMonitor(workspace_dir="/path/to/workspace")

# Detect changes in config files
changes = monitor.detect_config_changes(["config.yaml", "settings.json"])

# Create a snapshot for drift detection
snapshot = monitor.create_snapshot("production", ["config.yaml", "settings.json"])

# Later, detect drift against the snapshot
drift_report = monitor.detect_drift(snapshot.snapshot_id, ["config.yaml", "settings.json"])

# Audit configuration for compliance
audit = monitor.audit_configuration("production", ["config.yaml"])
print(audit.compliance_status)  # "compliant" or "non_compliant"
```

```python
from codomyrmex.config_management.monitoring.watcher import ConfigWatcher

# Watch a file for hot-reload
def on_change():
    print("Config file changed, reloading...")

watcher = ConfigWatcher("config.yaml", callback=on_change, interval=5)
watcher.start()
# ... later ...
watcher.stop()
```

## Architecture

```
monitoring/
  config_monitor.py   # ConfigurationMonitor, ConfigChange, ConfigAudit, ConfigSnapshot, monitor_config_changes
  watcher.py          # ConfigWatcher -- threaded mtime-based file change detection
  README.md
  AGENTS.md
  SPEC.md
```

## Testing

```bash
uv run pytest src/codomyrmex/tests/unit/config_management/ -v
```

## Navigation

- [AGENTS.md](AGENTS.md) | [SPEC.md](SPEC.md) | [Parent](../README.md)
