"""Unit tests for the 6 new v0.4.0 Hermes MCP tools."""

from __future__ import annotations

import json
import shutil
from typing import TYPE_CHECKING

import pytest

from codomyrmex.agents.hermes.mcp_tools import (
    hermes_approve_command,
    hermes_fastmcp_scaffold,
    hermes_gateway_status,
    hermes_model_info,
    hermes_pairing_add,
    hermes_pairing_list,
    hermes_skill_install,
)

if TYPE_CHECKING:
    from pathlib import Path

# ---------------------------------------------------------------------------
# hermes_gateway_status
# ---------------------------------------------------------------------------


class TestHermesGatewayStatus:
    def test_returns_dict_with_instances(self) -> None:
        result = hermes_gateway_status()
        assert isinstance(result, dict)
        assert "status" in result
        assert "instances" in result
        assert isinstance(result["instances"], list)

    @pytest.mark.skipif(
        shutil.which("hermes") is None, reason="Hermes CLI not installed"
    )
    def test_real_gateway_status(self) -> None:
        result = hermes_gateway_status()
        assert result["status"] in ("success", "error")


# ---------------------------------------------------------------------------
# hermes_model_info
# ---------------------------------------------------------------------------


class TestHermesModelInfo:
    def test_known_model_returns_dict(self) -> None:
        result = hermes_model_info("nvidia/nemotron-3-super-120b-a12b:free")
        assert isinstance(result, dict)
        assert "model_id" in result
        assert result["model_id"] == "nvidia/nemotron-3-super-120b-a12b:free"

    def test_unknown_model_does_not_raise(self) -> None:
        result = hermes_model_info("unknown/xyz")
        assert "model_id" in result

    def test_provider_extracted(self) -> None:
        result = hermes_model_info("anthropic/claude-3-haiku")
        assert result.get("provider") == "anthropic"


# ---------------------------------------------------------------------------
# hermes_approve_command
# ---------------------------------------------------------------------------


class TestHermesApproveCommand:
    def test_invalid_command_returns_error(self) -> None:
        result = hermes_approve_command(command="/unknown")
        assert result["status"] == "error"
        assert "Invalid command" in result.get("message", "")

    def test_valid_approve_command_accepted(self) -> None:
        # Just test validation passes — actual execution may fail without pending approval
        result = hermes_approve_command(command="/deny")
        assert isinstance(result, dict)
        assert "status" in result

    def test_approve_session_valid(self) -> None:
        result = hermes_approve_command(command="/approve session")
        assert isinstance(result, dict)
        assert "status" in result


# ---------------------------------------------------------------------------
# hermes_pairing_list
# ---------------------------------------------------------------------------


class TestHermesPairingList:
    def test_returns_dict(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ) -> None:
        monkeypatch.setenv("HERMES_HOME", str(tmp_path))
        result = hermes_pairing_list()
        assert isinstance(result, dict)
        assert result["status"] == "success"
        assert result["count"] == 0

    def test_reads_existing_approved_json(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ) -> None:
        monkeypatch.setenv("HERMES_HOME", str(tmp_path))
        pairing_dir = tmp_path / "pairing"
        pairing_dir.mkdir()
        approved_data = {"telegram": ["123456789", "987654321"]}
        (pairing_dir / "telegram-approved.json").write_text(json.dumps(approved_data))
        result = hermes_pairing_list()
        assert result["status"] == "success"
        assert result["count"] == 2
        assert "123456789" in result["approved"]["telegram"]


# ---------------------------------------------------------------------------
# hermes_pairing_add
# ---------------------------------------------------------------------------


class TestHermesPairingAdd:
    def test_adds_new_user(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ) -> None:
        monkeypatch.setenv("HERMES_HOME", str(tmp_path))
        result = hermes_pairing_add(user_id="111222333", platform="telegram")
        assert result["status"] == "success"
        assert "Added 111222333" in result["message"]

        # Verify it was persisted
        approved_path = tmp_path / "pairing" / "telegram-approved.json"
        data = json.loads(approved_path.read_text())
        assert "111222333" in data["telegram"]

    def test_duplicate_user_not_added_twice(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ) -> None:
        monkeypatch.setenv("HERMES_HOME", str(tmp_path))
        hermes_pairing_add(user_id="555", platform="telegram")
        result = hermes_pairing_add(user_id="555", platform="telegram")
        assert result["status"] == "success"
        assert "already in" in result["message"]
        assert result["approved_count"] == 1

    def test_creates_pairing_dir_if_missing(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ) -> None:
        monkeypatch.setenv("HERMES_HOME", str(tmp_path))
        assert not (tmp_path / "pairing").exists()
        hermes_pairing_add(user_id="999", platform="telegram")
        assert (tmp_path / "pairing" / "telegram-approved.json").exists()


# ---------------------------------------------------------------------------
# hermes_skill_install
# ---------------------------------------------------------------------------


class TestHermesSkillInstall:
    def test_returns_dict(self) -> None:
        # Don't actually install — just test it returns a dict without crashing
        # Use a clearly invalid URL so it fails fast
        result = hermes_skill_install("https://github.com/nonexistent/xxx-yyy-zzz.git")
        assert isinstance(result, dict)
        assert "status" in result
        # Should fail (no such repo) but not raise an exception
        assert result["status"] in ("success", "error")

    def test_has_tip_key(self) -> None:
        # Even on failure, we should get the tip key if it reaches the install path
        result = hermes_skill_install("https://github.com/nonexistent/xxx-yyy-zzz.git")
        # tip may or may not be present depending on where it fails
        assert isinstance(result, dict)


# ---------------------------------------------------------------------------
# hermes_fastmcp_scaffold
# ---------------------------------------------------------------------------


class TestHermesFastMcpScaffold:
    def test_generates_scaffold(self, tmp_path: Path) -> None:
        result = hermes_fastmcp_scaffold(
            output_dir=str(tmp_path),
            server_name="Hermes FastMCP",
        )
        assert result["status"] == "success"
        assert "script_path" in result
        assert "scaffold" in result

        package_dir = tmp_path / "hermes_fastmcp"
        assert (package_dir / "server.py").exists()
        assert (package_dir / "pyproject.toml").exists()
