"""Zero-mock tests for Configuration Monitoring module."""

import time

import pytest

from codomyrmex.config_monitoring.config_monitor import ConfigurationMonitor
from codomyrmex.config_monitoring.watcher import ConfigWatcher


@pytest.fixture
def workspace(tmp_path):
    return tmp_path


@pytest.fixture
def monitor(workspace):
    return ConfigurationMonitor(workspace_dir=workspace)


@pytest.mark.unit
class TestConfigurationMonitor:
    def test_calculate_file_hash(self, monitor, workspace):
        f = workspace / "test.txt"
        f.write_text("hello world")
        h1 = monitor.calculate_file_hash(f)
        assert len(h1) == 64

        f.write_text("hello world!")
        h2 = monitor.calculate_file_hash(f)
        assert h1 != h2

        assert monitor.calculate_file_hash(workspace / "nonexistent") == ""

    def test_detect_config_changes(self, monitor, workspace):
        f1 = workspace / "c1.yaml"
        f1.write_text("v1")

        # Initial detection (created)
        changes = monitor.detect_config_changes([f1])
        assert len(changes) == 1
        assert changes[0].change_type == "created"
        assert changes[0].config_path == str(f1.absolute())

        # No change detection
        changes = monitor.detect_config_changes([f1])
        assert len(changes) == 0

        # Modification detection
        time.sleep(0.01)  # Ensure change_id is unique if it uses time
        f1.write_text("v2")
        changes = monitor.detect_config_changes([f1])
        assert len(changes) == 1
        assert changes[0].change_type == "modified"
        assert changes[0].previous_hash is not None

        # Deletion detection
        f1.unlink()
        changes = monitor.detect_config_changes([f1])
        assert len(changes) == 1
        assert changes[0].change_type == "deleted"

    def test_snapshots_and_drift(self, monitor, workspace):
        config_dir = workspace / "configs"
        config_dir.mkdir()
        (config_dir / "a.yaml").write_text("a")
        (config_dir / "b.yaml").write_text("b")

        snapshot = monitor.create_snapshot("test", config_dir)
        assert snapshot.total_files == 2

        # No drift
        drift = monitor.detect_drift(snapshot.snapshot_id, config_dir)
        assert drift["drift_detected"] is False

        # Drift: modification
        (config_dir / "a.yaml").write_text("a_mod")
        drift = monitor.detect_drift(snapshot.snapshot_id, config_dir)
        assert drift["drift_detected"] is True
        assert drift["details"][0]["issue"] == "modified"

        # Drift: deletion
        (config_dir / "b.yaml").unlink()
        drift = monitor.detect_drift(snapshot.snapshot_id, config_dir)
        assert any(d["issue"] == "deleted" for d in drift["details"])

        # Drift: addition
        (config_dir / "c.yaml").write_text("c")
        drift = monitor.detect_drift(snapshot.snapshot_id, config_dir)
        assert any(d["issue"] == "added" for d in drift["details"])

    def test_audit_configuration(self, monitor, workspace):
        config_dir = workspace / "configs"
        config_dir.mkdir()

        # Secure file
        f_ok = config_dir / "ok.yaml"
        f_ok.write_text("safe: true")

        # Insecure file (sensitive data)
        f_bad = config_dir / "bad.yaml"
        f_bad.write_text("password: '12345'")

        audit = monitor.audit_configuration("test", config_dir)
        assert audit.compliance_status == "non_compliant"
        assert any("password" in issue for issue in audit.issues_found)

        # Check if audit is persisted
        monitor2 = ConfigurationMonitor(workspace_dir=workspace)
        history = monitor2.get_audit_history("test")
        assert len(history) >= 1

    def test_get_recent_changes(self, monitor, workspace):
        f = workspace / "f.yaml"
        f.write_text("v1")
        monitor.detect_config_changes([f])

        changes = monitor.get_recent_changes(1)
        assert len(changes) == 1

        changes_old = monitor.get_recent_changes(-1)  # effectively future
        assert len(changes_old) == 0


@pytest.mark.unit
class TestConfigWatcher:
    def test_watcher_callback(self, workspace):
        f = workspace / "watch.yaml"
        f.write_text("v1")

        results = []

        def callback():
            results.append(True)

        watcher = ConfigWatcher(f, callback, interval=0.1)
        watcher.start()
        assert watcher.is_alive

        try:
            time.sleep(0.2)
            f.write_text("v2")
            time.sleep(0.3)
            assert len(results) > 0
        finally:
            watcher.stop()

        assert not watcher.is_alive

    def test_watcher_file_disappears(self, workspace):
        f = workspace / "gone.yaml"
        f.write_text("here")

        watcher = ConfigWatcher(f, lambda: None, interval=0.1)
        watcher.start()

        try:
            f.unlink()
            time.sleep(0.2)
            # Should not crash, but _last_mtime should become 0
            assert watcher._last_mtime == 0
        finally:
            watcher.stop()
