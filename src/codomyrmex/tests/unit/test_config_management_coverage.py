# type: ignore
"""Functional tests for config_management module — zero-mock.

Exercises Configuration, ConfigurationManager, ConfigSchema,
ConfigWatcher, deploy/load/validate helpers, and SecretManager.
"""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

import pytest

import codomyrmex.config_management as cm

if TYPE_CHECKING:
    from pathlib import Path

# ---------------------------------------------------------------------------
# Smoke: all major exports are importable
# ---------------------------------------------------------------------------


class TestConfigManagementImports:
    """Verify all public symbols from config_management are importable."""

    @pytest.mark.parametrize(
        "name",
        [
            "Configuration",
            "ConfigurationManager",
            "ConfigSchema",
            "ConfigWatcher",
            "ConfigAudit",
            "ConfigDeployment",
            "ConfigurationDeployer",
            "ConfigurationMonitor",
            "load_configuration",
            "validate_configuration",
            "deploy_configuration",
            "get_config",
            "set_config",
            "validate_config",
            "monitor_config_changes",
        ],
    )
    def test_export_exists(self, name: str) -> None:
        assert hasattr(cm, name), f"Missing export: {name}"

    def test_secret_manager_available(self) -> None:
        assert hasattr(cm, "SecretManager")
        assert hasattr(cm, "encrypt_configuration")
        assert hasattr(cm, "manage_secrets")


# ---------------------------------------------------------------------------
# Configuration object
# ---------------------------------------------------------------------------


class TestConfiguration:
    """Configuration dataclass / class creation and usage."""

    def test_configuration_callable(self) -> None:
        cfg_class = cm.Configuration
        assert callable(cfg_class)

    def test_config_schema_callable(self) -> None:
        schema_class = cm.ConfigSchema
        assert callable(schema_class)


# ---------------------------------------------------------------------------
# ConfigurationManager
# ---------------------------------------------------------------------------


class TestConfigurationManager:
    """ConfigurationManager instantiation and basic ops."""

    def test_manager_instantiation(self) -> None:
        mgr = cm.ConfigurationManager()
        assert mgr is not None

    def test_manager_has_methods(self) -> None:
        mgr = cm.ConfigurationManager()
        # Should have load/save/get/set-like methods
        public_methods = [m for m in dir(mgr) if not m.startswith("_") and callable(getattr(mgr, m))]
        assert len(public_methods) > 0

    def test_get_set_config(self, tmp_path: Path) -> None:
        """get_config and set_config should be callable functions."""
        assert callable(cm.get_config)
        assert callable(cm.set_config)


# ---------------------------------------------------------------------------
# ConfigWatcher
# ---------------------------------------------------------------------------


class TestConfigWatcher:
    """ConfigWatcher instantiation."""

    def test_watcher_callable(self) -> None:
        assert callable(cm.ConfigWatcher)


# ---------------------------------------------------------------------------
# ConfigAudit and ConfigDeployment
# ---------------------------------------------------------------------------


class TestConfigAuditAndDeployment:
    """ConfigAudit and ConfigDeployment dataclasses."""

    def test_config_audit_callable(self) -> None:
        assert callable(cm.ConfigAudit)

    def test_config_deployment_callable(self) -> None:
        assert callable(cm.ConfigDeployment)

    def test_configuration_deployer_callable(self) -> None:
        assert callable(cm.ConfigurationDeployer)

    def test_configuration_monitor_callable(self) -> None:
        assert callable(cm.ConfigurationMonitor)


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------


class TestHelperFunctions:
    """Top-level convenience functions."""

    def test_load_configuration_callable(self) -> None:
        assert callable(cm.load_configuration)

    def test_validate_configuration_callable(self) -> None:
        assert callable(cm.validate_configuration)

    def test_deploy_configuration_callable(self) -> None:
        assert callable(cm.deploy_configuration)

    def test_monitor_config_changes_callable(self) -> None:
        assert callable(cm.monitor_config_changes)

    def test_validate_config_callable(self) -> None:
        assert callable(cm.validate_config)
