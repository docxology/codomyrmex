# Config Monitoring

Real-time configuration change detection, drift analysis, and compliance auditing.

> Source module: [`src/codomyrmex/config_monitoring/`](../../../src/codomyrmex/config_monitoring/)

## Key Capabilities

- **Change Detection**: Tracks modifications to configuration files using content hashing
- **Drift Detection**: Compares current config state against saved snapshots to identify drift
- **Compliance Auditing**: Runs security best-practice checks on configuration environments
- **Hot-Reloading**: Thread-safe, polling-based filesystem watcher for live config updates
- **Persistence**: Snapshots, hashes, and audit reports are persisted to disk across restarts

## Key Components

| Component | Purpose |
|-----------|---------|
| `ConfigurationMonitor` | Central orchestrator for change detection and auditing |
| `ConfigWatcher` | Thread-safe polling-based filesystem watcher |
| `ConfigSnapshot` | Point-in-time record of configuration states |
| `ConfigAudit` | Compliance report based on security best practices |

## Quick Start

```python
from codomyrmex.config_monitoring import ConfigurationMonitor

monitor = ConfigurationMonitor(workspace_dir="./data")
changes = monitor.detect_config_changes(["config/app.yaml"])
snapshot = monitor.create_snapshot("production", "config/")
drift = monitor.detect_drift(snapshot.snapshot_id, "config/")
audit = monitor.audit_configuration("production", "config/")
```

## MCP Tools

This module does not currently expose MCP tools. Use the Python API directly.

## References

- [Source README](../../../src/codomyrmex/config_monitoring/README.md)
- [AGENTS.md](../../../src/codomyrmex/config_monitoring/AGENTS.md)
- [PAI.md](../../../src/codomyrmex/config_monitoring/PAI.md)
