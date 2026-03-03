"""Zero-mock tests for Configuration Monitoring MCP tools."""

import time
from pathlib import Path

import pytest

from codomyrmex.config_monitoring.mcp_tools import (
    config_monitoring_audit_configuration,
    config_monitoring_create_snapshot,
    config_monitoring_detect_changes,
    config_monitoring_detect_drift,
)


@pytest.fixture
def workspace_dir(tmp_path: Path) -> str:
    """Provide a temporary workspace directory."""
    return str(tmp_path)


@pytest.mark.unit
def test_config_monitoring_detect_changes(workspace_dir: str):
    """Test detect_changes MCP tool without mocking."""
    config_file = Path(workspace_dir) / "app_config.json"
    config_file.write_text('{"key": "value"}')

    # Initial detection (created)
    changes = config_monitoring_detect_changes(
        config_paths=[str(config_file)], workspace_dir=workspace_dir
    )
    assert len(changes) == 1
    assert changes[0]["change_type"] == "created"
    assert changes[0]["config_path"] == str(config_file.absolute())

    # Detect again (no change)
    changes = config_monitoring_detect_changes(
        config_paths=[str(config_file)], workspace_dir=workspace_dir
    )
    assert len(changes) == 0

    # Modify file
    time.sleep(0.01)  # Ensure modification time/hash updates can be tested properly
    config_file.write_text('{"key": "value2"}')
    changes = config_monitoring_detect_changes(
        config_paths=[str(config_file)], workspace_dir=workspace_dir
    )
    assert len(changes) == 1
    assert changes[0]["change_type"] == "modified"


@pytest.mark.unit
def test_config_monitoring_create_snapshot_and_detect_drift(workspace_dir: str):
    """Test create_snapshot and detect_drift MCP tools together."""
    config_dir = Path(workspace_dir) / "config"
    config_dir.mkdir()
    f1 = config_dir / "conf1.json"
    f1.write_text('{"env": "prod"}')
    f2 = config_dir / "conf2.json"
    f2.write_text('{"db": "main"}')

    # Create snapshot
    snapshot_result = config_monitoring_create_snapshot(
        environment="production",
        config_dir=str(config_dir),
        workspace_dir=workspace_dir,
    )
    snapshot_id = snapshot_result["snapshot_id"]
    assert snapshot_result["environment"] == "production"
    assert snapshot_result["total_files"] == 2
    assert "config_hashes" in snapshot_result

    # Detect drift immediately (should be none)
    drift = config_monitoring_detect_drift(
        snapshot_id=snapshot_id, config_dir=str(config_dir), workspace_dir=workspace_dir
    )
    assert not drift["details"]



    # Modify f1, delete f2, add f3
    f1.write_text('{"env": "dev"}')
    f2.unlink()
    f3 = config_dir / "conf3.json"
    f3.write_text('{"cache": "redis"}')

    # Detect drift again
    drift2 = config_monitoring_detect_drift(
        snapshot_id=snapshot_id, config_dir=str(config_dir), workspace_dir=workspace_dir
    )
    issues = {d["path"]: d["issue"] for d in drift2["details"]}
    assert issues[str(f1.absolute())] == "modified"
    assert issues[str(f2.absolute())] == "deleted"
    assert issues[str(f3.absolute())] == "added"


@pytest.mark.unit
def test_config_monitoring_audit_configuration(workspace_dir: str):
    """Test audit_configuration MCP tool without mocking."""
    config_dir = Path(workspace_dir) / "config"
    config_dir.mkdir()

    # Secure file
    secure_file = config_dir / "app.json"
    secure_file.write_text('{"port": 8080}')

    # Insecure file with a hardcoded password
    insecure_file = config_dir / "db.json"
    insecure_file.write_text('password: "super_secret_password"')
    # Make insecure file too permissive (mimic by doing nothing, audit uses regex and permissions)
    # The audit_configuration in config_monitor.py checks for "password", "secret", "token", "key" in files
    # It also checks permissions if possible, but the regex will definitely trigger

    audit = config_monitoring_audit_configuration(
        environment="staging", config_dir=str(config_dir), workspace_dir=workspace_dir
    )

    assert audit["environment"] == "staging"
    assert "audit_id" in audit
    assert "timestamp" in audit

    # Based on ConfigMonitor implementation, this should find issues
    # "compliance_status" might be "non_compliant"
    assert audit["compliance_status"] == "non_compliant"
    assert len(audit["issues_found"]) > 0
    assert any(
        "password" in issue.lower() or "secret" in issue.lower()
        for issue in audit["issues_found"]
    )
