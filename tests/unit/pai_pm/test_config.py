"""Tests for pai_pm config defaults and env var overrides."""

from __future__ import annotations

import pytest

from codomyrmex.pai_pm.config import PaiPmConfig, get_config


@pytest.mark.unit
@pytest.mark.pai_pm
class TestPaiPmConfigDefaults:
    def test_default_port(self) -> None:
        cfg = PaiPmConfig()
        assert cfg.port == 8889

    def test_default_host(self) -> None:
        cfg = PaiPmConfig()
        assert cfg.host == "127.0.0.1"

    def test_default_startup_timeout(self) -> None:
        cfg = PaiPmConfig()
        assert cfg.startup_timeout == 10

    def test_default_request_timeout(self) -> None:
        cfg = PaiPmConfig()
        assert cfg.request_timeout == 30

    def test_server_script_contains_server_ts(self) -> None:
        cfg = PaiPmConfig()
        assert cfg.server_script.endswith("server.ts")

    def test_server_script_contains_pai_pm(self) -> None:
        cfg = PaiPmConfig()
        assert "pai_pm" in cfg.server_script


@pytest.mark.unit
@pytest.mark.pai_pm
class TestPaiPmConfigEnvOverrides:
    def test_port_from_env(self, monkeypatch) -> None:
        monkeypatch.setenv("PAI_PM_PORT", "9999")
        cfg = PaiPmConfig()
        assert cfg.port == 9999

    def test_host_from_env(self, monkeypatch) -> None:
        monkeypatch.setenv("PAI_PM_HOST", "0.0.0.0")
        cfg = PaiPmConfig()
        assert cfg.host == "0.0.0.0"

    def test_startup_timeout_from_env(self, monkeypatch) -> None:
        monkeypatch.setenv("PAI_PM_STARTUP_TIMEOUT", "60")
        cfg = PaiPmConfig()
        assert cfg.startup_timeout == 60

    def test_request_timeout_from_env(self, monkeypatch) -> None:
        monkeypatch.setenv("PAI_PM_REQUEST_TIMEOUT", "120")
        cfg = PaiPmConfig()
        assert cfg.request_timeout == 120

    def test_server_script_from_env(self, monkeypatch) -> None:
        monkeypatch.setenv("PAI_PM_SERVER_SCRIPT", "/custom/path/server.ts")
        cfg = PaiPmConfig()
        assert cfg.server_script == "/custom/path/server.ts"

    def test_get_config_returns_config_instance(self) -> None:
        cfg = get_config()
        assert isinstance(cfg, PaiPmConfig)
