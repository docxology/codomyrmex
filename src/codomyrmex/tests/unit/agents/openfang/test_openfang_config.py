"""Tests for OpenFangConfig — zero-mock, env-var driven."""

import os
from pathlib import Path

from codomyrmex.agents.openfang.config import (
    OpenFangConfig,
    _default_vendor_dir,
    get_config,
)


class TestOpenFangConfigDefaults:
    def test_default_command(self):
        cfg = OpenFangConfig()
        assert cfg.command == os.getenv("OPENFANG_COMMAND", "openfang")

    def test_default_timeout_is_int(self):
        cfg = OpenFangConfig()
        assert isinstance(cfg.timeout, int)
        assert cfg.timeout > 0

    def test_default_timeout_value(self):
        # Ensure env var isn't set for this test
        os.environ.pop("OPENFANG_TIMEOUT", None)
        cfg = OpenFangConfig()
        assert cfg.timeout == 120

    def test_default_gateway_url(self):
        os.environ.pop("OPENFANG_GATEWAY_URL", None)
        cfg = OpenFangConfig()
        assert cfg.gateway_url == "ws://localhost:3000"

    def test_default_install_dir(self):
        os.environ.pop("OPENFANG_INSTALL_DIR", None)
        cfg = OpenFangConfig()
        assert cfg.install_dir == "/usr/local/bin"

    def test_default_vendor_dir_contains_openfang(self):
        cfg = OpenFangConfig()
        assert "openfang" in cfg.vendor_dir.lower()

    def test_default_vendor_dir_is_absolute_path(self):
        cfg = OpenFangConfig()
        assert Path(cfg.vendor_dir).is_absolute()


class TestOpenFangConfigEnvOverrides:
    def test_command_override(self):
        os.environ["OPENFANG_COMMAND"] = "my_openfang"
        try:
            cfg = OpenFangConfig()
            assert cfg.command == "my_openfang"
        finally:
            os.environ.pop("OPENFANG_COMMAND", None)

    def test_timeout_override(self):
        os.environ["OPENFANG_TIMEOUT"] = "300"
        try:
            cfg = OpenFangConfig()
            assert cfg.timeout == 300
        finally:
            os.environ.pop("OPENFANG_TIMEOUT", None)

    def test_gateway_url_override(self):
        os.environ["OPENFANG_GATEWAY_URL"] = "ws://remote:9000"
        try:
            cfg = OpenFangConfig()
            assert cfg.gateway_url == "ws://remote:9000"
        finally:
            os.environ.pop("OPENFANG_GATEWAY_URL", None)

    def test_install_dir_override(self):
        os.environ["OPENFANG_INSTALL_DIR"] = "/opt/bin"
        try:
            cfg = OpenFangConfig()
            assert cfg.install_dir == "/opt/bin"
        finally:
            os.environ.pop("OPENFANG_INSTALL_DIR", None)


class TestOpenFangConfigProperties:
    def test_vendor_path_is_path_object(self):
        cfg = OpenFangConfig()
        assert isinstance(cfg.vendor_path, Path)

    def test_vendor_path_matches_vendor_dir(self):
        cfg = OpenFangConfig()
        assert str(cfg.vendor_path) == cfg.vendor_dir

    def test_is_submodule_initialized_returns_bool(self):
        cfg = OpenFangConfig()
        result = cfg.is_submodule_initialized
        assert isinstance(result, bool)

    def test_is_submodule_initialized_false_for_nonexistent(self):
        cfg = OpenFangConfig(vendor_dir="/tmp/nonexistent_openfang_xyz_9999")
        assert cfg.is_submodule_initialized is False

    def test_cargo_binary_is_path_object(self):
        cfg = OpenFangConfig()
        assert isinstance(cfg.cargo_binary, Path)

    def test_cargo_binary_path_contains_release(self):
        cfg = OpenFangConfig()
        assert "release" in str(cfg.cargo_binary)

    def test_cargo_binary_name(self):
        cfg = OpenFangConfig()
        assert cfg.cargo_binary.name == "openfang"


class TestDefaultVendorDir:
    def test_default_vendor_dir_function_returns_str(self):
        result = _default_vendor_dir()
        assert isinstance(result, str)

    def test_default_vendor_dir_ends_with_openfang(self):
        result = _default_vendor_dir()
        assert result.endswith("openfang")

    def test_vendor_dir_contains_vendor(self):
        result = _default_vendor_dir()
        assert "vendor" in result


class TestGetConfig:
    def test_get_config_returns_openfang_config(self):
        cfg = get_config()
        assert isinstance(cfg, OpenFangConfig)

    def test_get_config_creates_new_instance_each_call(self):
        cfg1 = get_config()
        cfg2 = get_config()
        assert cfg1 is not cfg2
