"""Unit tests for Hermes gateway module (codomyrmex.agents.hermes.gateway).

Zero-Mock Policy: tests verify real imports, class availability, and
production ConfigurationManager parsing/schema validation over public repository
defaults and isolated YAML policy. Operator configuration is never a test input;
these parser checks do not establish live gateway integration.
"""

from __future__ import annotations

import importlib
import json
from pathlib import Path

import pytest
from tests.support.repo_paths import REPO_ROOT

from codomyrmex.config_management.core.config_loader import (
    Configuration,
    ConfigurationManager,
)

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


@pytest.fixture
def gateway_configuration(hermes_test_home: Path) -> Configuration:
    """Parse/merge public defaults and isolated policy using the production loader."""
    schema = hermes_test_home / "schema.json"
    schema.write_text(
        json.dumps(
            {
                "type": "object",
                "required": ["module", "telegram", "approvals", "security"],
                "properties": {
                    "telegram": {
                        "type": "object",
                        "required": ["require_mention"],
                        "properties": {"require_mention": {"type": "boolean"}},
                    },
                    "approvals": {
                        "type": "object",
                        "required": ["mode"],
                        "properties": {"mode": {"enum": ["manual"]}},
                    },
                    "security": {
                        "type": "object",
                        "required": ["allow_private_urls"],
                        "properties": {"allow_private_urls": {"type": "boolean"}},
                    },
                },
            }
        ),
        encoding="utf-8",
    )
    manager = ConfigurationManager(config_dir=str(hermes_test_home))
    return manager.load_configuration(
        "gateway_fixture",
        sources=[str(REPO_ROOT / "config/agents/hermes.yaml"), "config.yaml"],
        schema_path=str(schema),
    )


class TestGatewayConfigLoading:
    """Verify actual YAML parsing, policy types, schema errors and source merging."""

    def test_hermes_config_yaml_exists(self, hermes_test_home: Path) -> None:
        assert (hermes_test_home / "config.yaml").stat().st_size > 0

    def test_hermes_config_yaml_parseable(
        self, gateway_configuration: Configuration
    ) -> None:
        assert gateway_configuration.validate() == []
        assert gateway_configuration.get_value("module") == "hermes"

    def test_config_has_telegram_section(
        self, gateway_configuration: Configuration
    ) -> None:
        assert gateway_configuration.get_value("telegram.require_mention") is True

    def test_config_telegram_has_require_mention(
        self, gateway_configuration: Configuration
    ) -> None:
        assert isinstance(
            gateway_configuration.get_value("telegram.require_mention"), bool
        )

    def test_config_has_approvals_section(
        self, gateway_configuration: Configuration
    ) -> None:
        assert gateway_configuration.get_value("approvals.mode") == "manual"

    def test_config_has_security_section(
        self, gateway_configuration: Configuration
    ) -> None:
        assert gateway_configuration.get_value("security.allow_private_urls") is False

    def test_isolated_policy_overrides_public_defaults(
        self, gateway_configuration: Configuration
    ) -> None:
        assert gateway_configuration.get_value("backend") == "none"
        assert gateway_configuration.get_value("dispatch.apply") is False
        assert gateway_configuration.get_value("model")
        assert gateway_configuration.source.endswith("config.yaml")

    def test_policy_schema_rejects_nonboolean_security(
        self, gateway_configuration: Configuration
    ) -> None:
        gateway_configuration.set_value("security.allow_private_urls", "false")
        errors = gateway_configuration.validate()
        assert errors
        assert any("allow_private_urls" in error for error in errors)

    def test_yaml_override_preserves_nested_policy(
        self, hermes_test_home: Path
    ) -> None:
        (hermes_test_home / "override.yaml").write_text(
            "telegram:\n  require_mention: false\n", encoding="utf-8"
        )
        manager = ConfigurationManager(config_dir=str(hermes_test_home))
        loaded = manager.load_configuration(
            "gateway_fixture", sources=["config.yaml", "override.yaml"]
        )
        assert loaded.get_value("telegram.require_mention") is False
        assert loaded.get_value("security.allow_private_urls") is False
        assert loaded.get_value("approvals.mode") == "manual"
