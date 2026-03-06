# Configuration Monitoring - Agent Coordination
**Version**: v1.1.4 | **Status**: Active | **Last Updated**: March 2026

## Overview

Agent coordination guide for the `config_management/monitoring` sub-module. Provides configuration change detection, drift analysis, compliance auditing, and hot-reload file watching for AI agents managing environment configurations.

## Key Files

| File | Purpose |
|------|---------|
| `config_monitor.py` | `ConfigurationMonitor` class with change detection, snapshot/drift, and auditing |
| `watcher.py` | `ConfigWatcher` -- background thread that monitors file mtime and fires a callback |

## MCP Tools Available

No MCP tools exposed directly from this sub-module. The parent `config_management` module exposes `get_config`, `set_config`, and `validate_config` via its own `mcp_tools.py`.

## Agent Instructions

1. Use `ConfigurationMonitor` to detect changes in configuration files via SHA-256 hash comparison. Call `detect_config_changes(paths)` with a list of file paths.
2. Create snapshots with `create_snapshot(environment, paths)` before making environment changes. Use `detect_drift(snapshot_id, current_paths)` to verify configuration consistency afterward.
3. Run `audit_configuration(environment, paths)` to check for overly permissive file permissions, exposed secrets (password/api_key/secret/token patterns), and missing required sections.
4. Use `ConfigWatcher` for hot-reload scenarios: it runs a daemon thread polling file mtime at a configurable interval (default 5 seconds).
5. The monitor persists hash state to `config_monitoring/config_hashes.json` and snapshots to `config_monitoring/snapshots/`. Audit results are saved to `config_audits/`.

## Operating Contracts

- **No Silent Fallbacks**: `detect_drift()` raises `CodomyrmexError` if the snapshot ID is not found. Hash store read failures log a warning and treat the run as a first scan.
- **Zero-Mock Policy**: Tests use real files on disk, not mocked file systems.
- **Explicit Failure**: Compliance issues are collected as string lists in `ConfigAudit.issues_found`, never silently swallowed.

## Common Patterns

```python
# Change detection workflow
monitor = ConfigurationMonitor(workspace_dir="/workspace")
changes = monitor.detect_config_changes(["app.yaml", "db.json"])
for change in changes:
    print(f"{change.change_type}: {change.config_path}")

# Drift detection workflow
snapshot = monitor.create_snapshot("staging", config_paths)
# ... deploy changes ...
drift = monitor.detect_drift(snapshot.snapshot_id, config_paths)
if drift["files_in_drift"] > 0:
    print("Configuration drift detected!")
```

## PAI Agent Role Access Matrix

| Agent Role | Access Level | Notes |
|------------|-------------|-------|
| Engineer | Full | Creates snapshots, runs audits, monitors changes |
| Architect | Read | Reviews drift reports and audit results |
| QATester | Read | Validates audit compliance in CI pipelines |

## Navigation

- [README.md](README.md) | [SPEC.md](SPEC.md) | [Parent](../README.md)
