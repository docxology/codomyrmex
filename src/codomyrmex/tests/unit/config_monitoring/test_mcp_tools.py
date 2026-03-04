"""Unit tests for config_monitoring MCP tools."""

from pathlib import Path

import pytest

from codomyrmex.config_monitoring.mcp_tools import (
    config_monitoring_audit,
    config_monitoring_create_snapshot,
    config_monitoring_detect_changes,
    config_monitoring_detect_drift,
)


@pytest.fixture
def workspace_dir(tmp_path: Path) -> Path:
    return tmp_path / "workspace"


@pytest.fixture
def config_dir(workspace_dir: Path) -> Path:
    config = workspace_dir / "config"
    config.mkdir(parents=True)
    return config


@pytest.mark.unit
def test_mcp_detect_changes(workspace_dir: Path, config_dir: Path) -> None:
    config_file = config_dir / "app.yaml"
    config_file.write_text("key: value")

    changes = config_monitoring_detect_changes([str(config_file)], str(workspace_dir))
    assert len(changes) == 1
    assert changes[0]["change_type"] == "created"

    config_file.write_text("key: new_value")
    changes2 = config_monitoring_detect_changes([str(config_file)], str(workspace_dir))
    assert len(changes2) == 1
    assert changes2[0]["change_type"] == "modified"


@pytest.mark.unit
def test_mcp_create_snapshot_and_drift(workspace_dir: Path, config_dir: Path) -> None:
    config_file = config_dir / "app.yaml"
    config_file.write_text("key: value")

    snapshot = config_monitoring_create_snapshot(
        "prod", str(config_dir), str(workspace_dir)
    )
    assert snapshot["environment"] == "prod"
    assert snapshot["total_files"] == 1

    drift = config_monitoring_detect_drift(
        snapshot["snapshot_id"], str(config_dir), str(workspace_dir)
    )
    assert drift["drift_detected"] is False

    config_file.write_text("key: new_value")
    drift_after = config_monitoring_detect_drift(
        snapshot["snapshot_id"], str(config_dir), str(workspace_dir)
    )
    assert drift_after["drift_detected"] is True


@pytest.mark.unit
def test_mcp_audit(workspace_dir: Path, config_dir: Path) -> None:
    secret_file = config_dir / "secrets.yaml"
    secret_file.write_text("password: 'supersecret'")

    audit = config_monitoring_audit("prod", str(config_dir), str(workspace_dir))
    assert audit["environment"] == "prod"
    assert audit["compliance_status"] == "non_compliant"
    assert len(audit["issues_found"]) > 0
