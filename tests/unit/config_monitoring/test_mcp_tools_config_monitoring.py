"""Tests for config_monitoring MCP tools."""

import os
import tempfile

from codomyrmex.config_monitoring.mcp_tools import (
    config_monitoring_detect_changes,
    config_monitoring_hash_file,
    config_monitoring_summary,
)


class TestConfigMonitoringDetectChanges:
    def test_returns_dict_with_status(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = os.path.join(tmpdir, "test.conf")
            with open(config_file, "w") as f:
                f.write("key=value\n")
            result = config_monitoring_detect_changes(
                config_paths=[config_file],
                workspace_dir=tmpdir,
            )
        assert isinstance(result, dict)
        assert "status" in result

    def test_new_file_detected_as_created(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = os.path.join(tmpdir, "app.conf")
            with open(config_file, "w") as f:
                f.write("setting=true\n")
            result = config_monitoring_detect_changes(
                config_paths=[config_file],
                workspace_dir=tmpdir,
            )
        assert result["status"] == "success"
        assert result["changes_detected"] >= 1
        assert result["changes"][0]["change_type"] == "created"

    def test_no_change_on_second_scan(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = os.path.join(tmpdir, "app.conf")
            with open(config_file, "w") as f:
                f.write("setting=true\n")
            # First scan registers the file
            config_monitoring_detect_changes(
                config_paths=[config_file],
                workspace_dir=tmpdir,
            )
            # Second scan should detect no changes
            result = config_monitoring_detect_changes(
                config_paths=[config_file],
                workspace_dir=tmpdir,
            )
        assert result["status"] == "success"
        assert result["changes_detected"] == 0

    def test_empty_paths_list(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            result = config_monitoring_detect_changes(
                config_paths=[],
                workspace_dir=tmpdir,
            )
        assert result["status"] == "success"
        assert result["changes_detected"] == 0


class TestConfigMonitoringSummary:
    def test_returns_dict_with_status(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            result = config_monitoring_summary(workspace_dir=tmpdir)
        assert isinstance(result, dict)
        assert result["status"] == "success"

    def test_summary_has_expected_keys(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            result = config_monitoring_summary(workspace_dir=tmpdir)
        summary = result["summary"]
        assert "total_snapshots" in summary
        assert "total_changes" in summary
        assert "status" in summary


class TestConfigMonitoringHashFile:
    def test_returns_dict_with_status(self):
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
            f.write("test content")
            f.flush()
            result = config_monitoring_hash_file(file_path=f.name)
        os.unlink(f.name)
        assert isinstance(result, dict)
        assert "status" in result

    def test_hash_is_sha256(self):
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
            f.write("test content")
            f.flush()
            result = config_monitoring_hash_file(file_path=f.name)
        os.unlink(f.name)
        assert result["status"] == "success"
        assert len(result["sha256"]) == 64  # SHA-256 hex digest length

    def test_nonexistent_file_returns_error(self):
        result = config_monitoring_hash_file(file_path="/nonexistent/file.conf")
        assert result["status"] == "error"

    def test_same_content_same_hash(self):
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix="_a") as f1:
            f1.write("identical")
            f1.flush()
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix="_b") as f2:
            f2.write("identical")
            f2.flush()
        r1 = config_monitoring_hash_file(file_path=f1.name)
        r2 = config_monitoring_hash_file(file_path=f2.name)
        os.unlink(f1.name)
        os.unlink(f2.name)
        assert r1["sha256"] == r2["sha256"]
