"""Unit tests for Hermes gateway module (codomyrmex.agents.hermes.gateway).

Zero-Mock Policy: tests verify real imports, class availability, and
configuration parsing from the local Codomyrmex gateway wrapper module.
"""

from __future__ import annotations

import importlib

import pytest

# ---------------------------------------------------------------------------
# Module importability
# ---------------------------------------------------------------------------


class TestGatewayModuleImport:
    """Verify gateway sub-modules import cleanly."""

    def test_gateway_init_importable(self) -> None:
        mod = importlib.import_module("codomyrmex.agents.hermes.gateway")
        assert mod is not None

    def test_gateway_server_importable(self) -> None:
        mod = importlib.import_module("codomyrmex.agents.hermes.gateway.server")
        assert mod is not None

    def test_gateway_cron_importable(self) -> None:
        mod = importlib.import_module("codomyrmex.agents.hermes.gateway.cron")
        assert mod is not None

    def test_gateway_directory_importable(self) -> None:
        mod = importlib.import_module("codomyrmex.agents.hermes.gateway.directory")
        assert mod is not None

    def test_gateway_identity_importable(self) -> None:
        mod = importlib.import_module("codomyrmex.agents.hermes.gateway.identity")
        assert mod is not None

    def test_gateway_memory_importable(self) -> None:
        mod = importlib.import_module("codomyrmex.agents.hermes.gateway.memory")
        assert mod is not None

    def test_gateway_sandbox_importable(self) -> None:
        mod = importlib.import_module("codomyrmex.agents.hermes.gateway.sandbox")
        assert mod is not None


# ---------------------------------------------------------------------------
# Gateway server classes
# ---------------------------------------------------------------------------


class TestGatewayServerClasses:
    """Verify expected classes exist in gateway.server."""

    def test_has_gateway_runner_class(self) -> None:
        mod = importlib.import_module("codomyrmex.agents.hermes.gateway.server")
        assert hasattr(mod, "GatewayRunner")


# ---------------------------------------------------------------------------
# Gateway directory
# ---------------------------------------------------------------------------


class TestGatewayDirectory:
    """Verify channel directory structures."""

    def test_directory_module_has_expected_exports(self) -> None:
        mod = importlib.import_module("codomyrmex.agents.hermes.gateway.directory")
        # Should have some kind of directory building capability
        public = [name for name in dir(mod) if not name.startswith("_")]
        assert len(public) > 0


# ---------------------------------------------------------------------------
# Gateway identity
# ---------------------------------------------------------------------------


class TestGatewayIdentity:
    """Verify identity/persona loading."""

    def test_identity_module_has_exports(self) -> None:
        mod = importlib.import_module("codomyrmex.agents.hermes.gateway.identity")
        public = [name for name in dir(mod) if not name.startswith("_")]
        assert len(public) > 0


# ---------------------------------------------------------------------------
# Gateway cron
# ---------------------------------------------------------------------------


class TestGatewayCron:
    """Verify cron scheduling structures."""

    def test_cron_module_has_exports(self) -> None:
        mod = importlib.import_module("codomyrmex.agents.hermes.gateway.cron")
        public = [name for name in dir(mod) if not name.startswith("_")]
        assert len(public) > 0


# ---------------------------------------------------------------------------
# Gateway memory
# ---------------------------------------------------------------------------


class TestGatewayMemory:
    """Verify memory management structures."""

    def test_memory_module_has_exports(self) -> None:
        mod = importlib.import_module("codomyrmex.agents.hermes.gateway.memory")
        public = [name for name in dir(mod) if not name.startswith("_")]
        assert len(public) > 0


# ---------------------------------------------------------------------------
# Gateway sandbox
# ---------------------------------------------------------------------------


class TestGatewaySandbox:
    """Verify sandbox isolation structures."""

    def test_sandbox_module_has_exports(self) -> None:
        mod = importlib.import_module("codomyrmex.agents.hermes.gateway.sandbox")
        public = [name for name in dir(mod) if not name.startswith("_")]
        assert len(public) > 0


# ---------------------------------------------------------------------------
# Config YAML loading
# ---------------------------------------------------------------------------


class TestGatewayConfigLoading:
    """Verify gateway configuration parsing."""

    def test_hermes_config_yaml_exists(self) -> None:
        from pathlib import Path

        config_path = Path.home() / ".hermes" / "config.yaml"
        if not config_path.exists():
            pytest.skip("~/.hermes/config.yaml not found")
        assert config_path.stat().st_size > 0

    def test_hermes_config_yaml_parseable(self) -> None:
        from pathlib import Path

        import yaml

        config_path = Path.home() / ".hermes" / "config.yaml"
        if not config_path.exists():
            pytest.skip("~/.hermes/config.yaml not found")

        config = yaml.safe_load(config_path.read_text())
        assert isinstance(config, dict)

    def test_config_has_telegram_section(self) -> None:
        from pathlib import Path

        import yaml

        config_path = Path.home() / ".hermes" / "config.yaml"
        if not config_path.exists():
            pytest.skip("~/.hermes/config.yaml not found")

        config = yaml.safe_load(config_path.read_text())
        assert "telegram" in config

    def test_config_telegram_has_require_mention(self) -> None:
        from pathlib import Path

        import yaml

        config_path = Path.home() / ".hermes" / "config.yaml"
        if not config_path.exists():
            pytest.skip("~/.hermes/config.yaml not found")

        config = yaml.safe_load(config_path.read_text())
        telegram = config.get("telegram", {})
        assert "require_mention" in telegram

    def test_config_has_approvals_section(self) -> None:
        from pathlib import Path

        import yaml

        config_path = Path.home() / ".hermes" / "config.yaml"
        if not config_path.exists():
            pytest.skip("~/.hermes/config.yaml not found")

        config = yaml.safe_load(config_path.read_text())
        assert "approvals" in config

    def test_config_has_security_section(self) -> None:
        from pathlib import Path

        import yaml

        config_path = Path.home() / ".hermes" / "config.yaml"
        if not config_path.exists():
            pytest.skip("~/.hermes/config.yaml not found")

        config = yaml.safe_load(config_path.read_text())
        assert "security" in config
