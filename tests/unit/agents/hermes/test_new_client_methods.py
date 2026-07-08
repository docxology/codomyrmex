"""Unit tests for the new HermesClient v0.4.0 methods."""

from __future__ import annotations

import shutil

import pytest

from codomyrmex.agents.hermes.hermes_client import HermesClient


@pytest.fixture
def client() -> HermesClient:
    """Minimal HermesClient for testing; CLI availability probed automatically."""
    return HermesClient(config={})


# ---------------------------------------------------------------------------
# get_gateway_status
# ---------------------------------------------------------------------------


class TestGetGatewayStatus:
    def test_no_cli_returns_error(
        self, monkeypatch: pytest.MonkeyPatch, client: HermesClient
    ) -> None:
        monkeypatch.setattr(client, "_cli_available", False)
        result = client.get_gateway_status()
        assert result["success"] is False
        assert "instances" in result
        assert result["instances"] == []

    @pytest.mark.skipif(
        shutil.which("hermes") is None, reason="Hermes CLI not installed"
    )
    def test_cli_returns_dict(self, client: HermesClient) -> None:
        result = client.get_gateway_status()
        assert "success" in result
        assert "instances" in result
        assert isinstance(result["instances"], list)


# ---------------------------------------------------------------------------
# get_model_info
# ---------------------------------------------------------------------------


class TestGetModelInfo:
    def test_unknown_model_does_not_raise(self, client: HermesClient) -> None:
        result = client.get_model_info("unknown/model-xyz")
        assert "model_id" in result
        assert result["model_id"] == "unknown/model-xyz"
        assert "context_length" in result

    def test_provider_extracted_from_model_id(self, client: HermesClient) -> None:
        result = client.get_model_info("nvidia/nemotron-3-super-120b-a12b:free")
        assert result.get("provider") == "nvidia"

    def test_model_without_slash(self, client: HermesClient) -> None:
        result = client.get_model_info("hermes3")
        assert result.get("provider") == "unknown"
        assert "model_id" in result

    @pytest.mark.skipif(
        shutil.which("hermes") is None, reason="Hermes CLI not installed"
    )
    def test_nemotron_info_real(self, client: HermesClient) -> None:
        """Integration: real model lookup for the current default model."""
        result = client.get_model_info("nvidia/nemotron-3-super-120b-a12b:free")
        assert "model_id" in result
        # We just ensure it doesn't crash; context_length may or may not be populated
        assert isinstance(result.get("context_length", 0), int)


# ---------------------------------------------------------------------------
# send_gateway_command
# ---------------------------------------------------------------------------


class TestSendGatewayCommand:
    def test_no_cli_returns_error(
        self, monkeypatch: pytest.MonkeyPatch, client: HermesClient
    ) -> None:
        monkeypatch.setattr(client, "_cli_available", False)
        result = client.send_gateway_command("/approve")
        assert result["success"] is False
        assert "Hermes CLI not available" in result.get("error", "")

    @pytest.mark.skipif(
        shutil.which("hermes") is None, reason="Hermes CLI not installed"
    )
    def test_deny_command_real(self, client: HermesClient) -> None:
        """Integration: sends /deny (safe no-op when no pending approval)."""
        result = client.send_gateway_command("/deny")
        # May fail if no approval pending — that's fine; we test it doesn't crash
        assert "success" in result


# ---------------------------------------------------------------------------
# install_skill
# ---------------------------------------------------------------------------


class TestInstallSkill:
    def test_no_cli_returns_error(
        self, monkeypatch: pytest.MonkeyPatch, client: HermesClient
    ) -> None:
        monkeypatch.setattr(client, "_cli_available", False)
        result = client.install_skill("https://github.com/example/skill.git")
        assert result["success"] is False
        assert "Hermes CLI not available" in result.get("error", "")

    @pytest.mark.skipif(
        shutil.which("hermes") is None, reason="Hermes CLI not installed"
    )
    def test_bad_url_returns_error(self, client: HermesClient) -> None:
        """Integration: invalid URL should fail gracefully."""
        result = client.install_skill("https://github.com/nonexistent/xxxxxxxx.git")
        assert isinstance(result, dict)
        assert "success" in result
        # Either it fails cleanly or raises subprocess error caught in dict


# ---------------------------------------------------------------------------
# scaffold_fastmcp
# ---------------------------------------------------------------------------


class TestScaffoldFastMcp:
    def test_generates_fastmcp_scaffold(self, tmp_path, client: HermesClient) -> None:
        result = client.scaffold_fastmcp(
            output_dir=str(tmp_path),
            server_name="Codomyrmex Demo",
        )
        assert result["success"] is True
        assert "script_path" in result

        package_dir = tmp_path / "codomyrmex_demo"
        assert (package_dir / "server.py").exists()
        assert (package_dir / "pyproject.toml").exists()
        assert (package_dir / "README.md").exists()

    def test_refuses_overwrite_without_force(
        self, tmp_path, client: HermesClient
    ) -> None:
        first = client.scaffold_fastmcp(
            output_dir=str(tmp_path),
            server_name="Codomyrmex Demo",
        )
        assert first["success"] is True

        second = client.scaffold_fastmcp(
            output_dir=str(tmp_path),
            server_name="Codomyrmex Demo",
        )
        assert second["success"] is False
        assert "Refusing to overwrite existing file" in second.get("error", "")
