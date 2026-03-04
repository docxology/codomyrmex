"""Unit tests for config_monitoring MCP tools."""

from pathlib import Path

import pytest

from codomyrmex.config_monitoring.mcp_tools import (
    config_monitoring_detect_changes,
    config_monitoring_hash_file,
    config_monitoring_summary,
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
    """Test detecting configuration changes via MCP."""
    config_file = config_dir / "app.yaml"
    config_file.write_text("key: value")

    changes = config_monitoring_detect_changes([str(config_file)], str(workspace_dir))
    assert changes["status"] == "success"
    assert changes["paths_checked"] == 1
    assert changes["changes_detected"] == 1
    assert changes["changes"][0]["change_type"] == "created"

    # Modify and check again
    config_file.write_text("key: new_value")
    changes2 = config_monitoring_detect_changes([str(config_file)], str(workspace_dir))
    assert changes2["status"] == "success"
    assert changes2["changes_detected"] == 1
    assert changes2["changes"][0]["change_type"] == "modified"


@pytest.mark.unit
def test_mcp_summary(workspace_dir: Path) -> None:
    """Test getting monitoring summary via MCP."""
    summary = config_monitoring_summary(str(workspace_dir))
    assert summary["status"] == "success"
    assert isinstance(summary["summary"], dict)


@pytest.mark.unit
def test_mcp_hash_file(config_dir: Path) -> None:
    """Test hashing a file via MCP."""
    config_file = config_dir / "app.yaml"
    config_file.write_text("key: value")

    result = config_monitoring_hash_file(str(config_file))
    assert result["status"] == "success"
    assert result["file_path"] == str(config_file)
    assert "sha256" in result

    # Non-existent file
    bad_result = config_monitoring_hash_file(str(config_dir / "missing.yaml"))
    assert bad_result["status"] == "error"
    assert "File not found" in bad_result["message"]
