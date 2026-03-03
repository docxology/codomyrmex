#!/usr/bin/env python3
"""
Orchestrator script for Configuration Monitoring.
Demonstrates change detection, snapshots, drift analysis, auditing, and watching.
"""

import time

from codomyrmex.config_monitoring import ConfigurationMonitor, ConfigWatcher


def main():
    # Auto-injected: Load configuration
    from pathlib import Path

    import yaml
    config_path = Path(__file__).resolve().parent.parent.parent / "config" / "config_monitoring" / "config.yaml"
    config_data = {}
    if config_path.exists():
        with open(config_path) as f:
            config_data = yaml.safe_load(f) or {}
            print(f"Loaded config from {config_path.name}")

    workspace = Path("config_monitoring_demo")
    workspace.mkdir(exist_ok=True)

    config_dir = workspace / "configs"
    config_dir.mkdir(exist_ok=True)

    # 1. Create initial config
    app_config = config_dir / "app.yaml"
    app_config.write_text("app:\n  name: Codomyrmex\n  version: 1.0.0\n")

    db_config = config_dir / "database.yaml"
    db_config.write_text("database:\n  host: localhost\n  port: 5432\n")

    print(f"--- Initialized demo in {workspace} ---")

    # 2. Initialize Monitor
    monitor = ConfigurationMonitor(workspace_dir=workspace)

    # 3. Detect changes (first run)
    print("\n[1] Detecting initial configuration...")
    changes = monitor.detect_config_changes([app_config, db_config])
    for c in changes:
        print(f"  {c.change_type.upper()}: {c.config_path}")

    # 4. Create Snapshot
    print("\n[2] Creating 'v1.0' snapshot...")
    snapshot = monitor.create_snapshot("prod", config_dir)
    print(f"  Snapshot created: {snapshot.snapshot_id} ({snapshot.total_files} files)")

    # 5. Modify config and detect drift
    print("\n[3] Modifying config and detecting drift...")
    time.sleep(1.1) # Ensure timestamp change
    db_config.write_text("database:\n  host: production-db\n  port: 5432\n  password: 'REDACTED_BUT_INSECURE'\n")

    drift = monitor.detect_drift(snapshot.snapshot_id, config_dir)
    print(f"  Drift detected: {drift['drift_detected']}")
    for d in drift['details']:
        print(f"  - {d['issue']}: {Path(d['path']).name}")

    # 6. Run Compliance Audit
    print("\n[4] Running compliance audit...")
    audit = monitor.audit_configuration("prod", config_dir)
    print(f"  Compliance Status: {audit.compliance_status.upper()}")
    if audit.issues_found:
        print("  Issues found:")
        for issue in audit.issues_found:
            print(f"    - {issue}")

    # 7. Demonstrate Watcher (briefly)
    print("\n[5] Starting ConfigWatcher for hot-reload demo (5 seconds)...")
    def on_change():
        print("  >> CALLBACK: Config file changed! Hot-reloading...")

    watcher = ConfigWatcher(app_config, on_change, interval=1.0)
    watcher.start()

    time.sleep(1.5)
    print("  Updating app.yaml...")
    app_config.write_text("app:\n  name: Codomyrmex\n  version: 1.0.1\n")

    time.sleep(2.0)
    watcher.stop()

    print("\n--- Demo Complete ---")
    summary = monitor.get_monitoring_summary()
    print(f"Final Summary: {summary}")

if __name__ == "__main__":
    main()
