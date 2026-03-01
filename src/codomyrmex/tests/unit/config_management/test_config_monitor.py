"""Zero-Mock tests for ConfigurationMonitor hash persistence.

Tests _get_previous_hash and _persist_hashes with real filesystem I/O.
"""


import pytest

from codomyrmex.config_management.monitoring.config_monitor import (
    ConfigurationMonitor,
)


@pytest.mark.unit
class TestConfigMonitorHashPersistence:
    """Test suite for config change detection hash persistence."""

    def test_get_previous_hash_no_store(self, tmp_path):
        """First run: no hash store file exists, should return None."""
        monitor = ConfigurationMonitor(workspace_dir=str(tmp_path))
        result = monitor._get_previous_hash("/some/config.yaml")
        assert result is None

    def test_persist_and_retrieve(self, tmp_path):
        """Persist hashes, then retrieve them."""
        monitor = ConfigurationMonitor(workspace_dir=str(tmp_path))
        monitor.monitoring_dir.mkdir(parents=True, exist_ok=True)

        hashes = {"/etc/app.yaml": "abc123", "/etc/db.conf": "def456"}
        monitor._persist_hashes(hashes)

        # Verify file exists
        store = monitor.monitoring_dir / "config_hashes.json"
        assert store.exists()

        # Read back
        assert monitor._get_previous_hash("/etc/app.yaml") == "abc123"
        assert monitor._get_previous_hash("/etc/db.conf") == "def456"
        assert monitor._get_previous_hash("/etc/missing.conf") is None

    def test_persist_merges_existing(self, tmp_path):
        """Persisting new hashes should merge with existing, not replace."""
        monitor = ConfigurationMonitor(workspace_dir=str(tmp_path))
        monitor.monitoring_dir.mkdir(parents=True, exist_ok=True)

        monitor._persist_hashes({"/a": "hash_a"})
        monitor._persist_hashes({"/b": "hash_b"})

        assert monitor._get_previous_hash("/a") == "hash_a"
        assert monitor._get_previous_hash("/b") == "hash_b"

    def test_persist_updates_existing_key(self, tmp_path):
        """Persisting a key that already exists should update its value."""
        monitor = ConfigurationMonitor(workspace_dir=str(tmp_path))
        monitor.monitoring_dir.mkdir(parents=True, exist_ok=True)

        monitor._persist_hashes({"/a": "v1"})
        monitor._persist_hashes({"/a": "v2"})

        assert monitor._get_previous_hash("/a") == "v2"

    def test_corrupted_store_returns_none(self, tmp_path):
        """If the hash store is corrupted JSON, return None gracefully."""
        monitor = ConfigurationMonitor(workspace_dir=str(tmp_path))
        monitor.monitoring_dir.mkdir(parents=True, exist_ok=True)

        store = monitor.monitoring_dir / "config_hashes.json"
        store.write_text("NOT VALID JSON {{{")

        result = monitor._get_previous_hash("/any/file")
        assert result is None
