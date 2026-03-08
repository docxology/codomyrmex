# Monitoring

**Version**: v1.1.9 | **Status**: Active | **Last Updated**: March 2026

## Overview
This directory contains the real, functional implementations and components for the `Monitoring` module within the Codomyrmex ecosystem. It provides tools for tracking configuration changes, detecting drift, performing compliance audits, and hot-reloading configurations.

## Principles
- **Functional Integrity**: All methods and classes within this directory are designed to be fully operational and production-ready.
- **Zero-Mock Policy**: Code herein adheres to the strict Zero-Mock testing policy, ensuring all tests run against real logic and filesystem interactions.
- **Persistence**: Change hashes, snapshots, and audit reports are persisted to disk to allow for long-term tracking and drift detection across restarts.

## Key Components
- `ConfigurationMonitor`: The central orchestrator for change detection and auditing.
- `ConfigWatcher`: A thread-safe, polling-based filesystem watcher for hot-reloading.
- `ConfigSnapshot`: A point-in-time record of configuration states.
- `ConfigAudit`: A compliance report based on security best practices.

## Usage Example
```python
from codomyrmex.config_monitoring import ConfigurationMonitor

monitor = ConfigurationMonitor(workspace_dir="./data")
changes = monitor.detect_config_changes(["config/app.yaml"])
snapshot = monitor.create_snapshot("production", "config/")
drift = monitor.detect_drift(snapshot.snapshot_id, "config/")
audit = monitor.audit_configuration("production", "config/")
```
