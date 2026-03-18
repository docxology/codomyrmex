# config_monitoring

**Version**: v1.2.3 | **Status**: Active | **Last Updated**: March 2026

## Overview

Configuration change detection, drift analysis, compliance auditing, and hot-reload watching. Tracks configuration file mutations via SHA-256 hashing, maintains point-in-time snapshots for infrastructure drift detection, scans for security anti-patterns (plaintext secrets, overly permissive file permissions), and provides a thread-safe filesystem watcher for hot-reload workflows.

## Key Components

| Component | File | Description |
| :--- | :--- | :--- |
| `ConfigurationMonitor` | `config_monitor.py` | Central monitoring engine: change detection, snapshots, drift, auditing |
| `ConfigWatcher` | `watcher.py` | Thread-safe daemon poller for single-file hot-reload |
| `ConfigChange` | `config_monitor.py` | Dataclass: single file mutation record |
| `ConfigSnapshot` | `config_monitor.py` | Dataclass: point-in-time directory hash capture |
| `ConfigAudit` | `config_monitor.py` | Dataclass: compliance audit result |
| `monitor_config_changes` | `config_monitor.py` | Convenience function: one-shot change detection |

## Quick Start

```python
from codomyrmex.config_monitoring import ConfigurationMonitor, ConfigWatcher

# Detect changes
monitor = ConfigurationMonitor(workspace_dir="/tmp/project")
changes = monitor.detect_config_changes(["config.yaml", "settings.json"])

# Take a snapshot for drift detection
snapshot = monitor.create_snapshot("production", "/etc/myapp/")

# Watch a file for hot-reload
watcher = ConfigWatcher("config.yaml", lambda: print("changed!"))
watcher.start()
```

## MCP Tools

| Tool | Description |
| :--- | :--- |
| `config_monitoring_detect_changes` | Detect config file changes by hashing |
| `config_monitoring_summary` | Get monitoring state summary |
| `config_monitoring_hash_file` | Compute SHA-256 hash of a file |

## Directory Contents

| File | Purpose |
| :--- | :--- |
| `config_monitor.py` | Core monitoring engine (560 lines) |
| `watcher.py` | Hot-reload file watcher (94 lines) |
| `mcp_tools.py` | MCP tool definitions (3 tools) |
| `__init__.py` | Public exports |

## Navigation

- **Parent Directory**: [codomyrmex](../README.md)
- **Documentation**: [SPEC.md](SPEC.md) | [API_SPECIFICATION.md](API_SPECIFICATION.md) | [PAI.md](PAI.md) | [AGENTS.md](AGENTS.md)
- **Project Root**: [../../../README.md](../../../README.md)
