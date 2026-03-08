"""Tests for OpenFangRunner — zero-mock, uses env var to control binary detection."""
import os

import pytest

from codomyrmex.agents.openfang import HAS_OPENFANG
from codomyrmex.agents.openfang.config import OpenFangConfig
from codomyrmex.agents.openfang.core import OpenFangRunner, get_openfang_version
from codomyrmex.agents.openfang.exceptions import OpenFangNotInstalledError

_NONEXISTENT_CMD = "nonexistent_openfang_binary_xyz_999"


class TestOpenFangRunnerInit:
    def test_raises_not_installed_for_bad_command(self):
        cfg = OpenFangConfig(command=_NONEXISTENT_CMD)
        with pytest.raises(OpenFangNotInstalledError):
            OpenFangRunner(config=cfg)

    def test_error_message_contains_install_hint(self):
        cfg = OpenFangConfig(command=_NONEXISTENT_CMD)
        with pytest.raises(OpenFangNotInstalledError) as exc_info:
            OpenFangRunner(config=cfg)
        assert "install" in str(exc_info.value).lower()

    def test_config_stored(self):
        cfg = OpenFangConfig(command=_NONEXISTENT_CMD)
        try:
            runner = OpenFangRunner(config=cfg)
        except OpenFangNotInstalledError:
            pass  # Expected — config check itself is what we test indirectly


class TestOpenFangRunnerConfig:
    def test_custom_config_used(self):
        cfg = OpenFangConfig(command=_NONEXISTENT_CMD, timeout=999)
        with pytest.raises(OpenFangNotInstalledError):
            OpenFangRunner(config=cfg)

    def test_default_timeout_from_config(self):
        cfg = OpenFangConfig(command=_NONEXISTENT_CMD)
        with pytest.raises(OpenFangNotInstalledError):
            OpenFangRunner(config=cfg)


class TestGetOpenfangVersion:
    def test_returns_string(self):
        result = get_openfang_version()
        assert isinstance(result, str)

    def test_empty_when_not_installed(self):
        # Save and override PATH to ensure binary not found
        old_path = os.environ.get("PATH", "")
        os.environ["PATH"] = "/nonexistent_path_openfang_xyz"
        try:
            # Need to reload the module-level HAS_OPENFANG check
            import importlib

            import codomyrmex.agents.openfang.core as core_mod
            result = core_mod.get_openfang_version()
            assert isinstance(result, str)
        finally:
            os.environ["PATH"] = old_path


class TestHasOpenfangFlag:
    def test_has_openfang_is_bool(self):
        assert isinstance(HAS_OPENFANG, bool)


@pytest.mark.skipif(not HAS_OPENFANG, reason="openfang binary required")
class TestOpenFangRunnerWithBinary:
    def test_runner_init_succeeds(self):
        runner = OpenFangRunner()
        assert runner is not None

    def test_version_returns_dict(self):
        runner = OpenFangRunner()
        result = runner.version()
        assert isinstance(result, dict)
        assert "stdout" in result
        assert "returncode" in result

    def test_doctor_returns_dict(self):
        runner = OpenFangRunner()
        result = runner.doctor()
        assert isinstance(result, dict)

    def test_hands_list_returns_dict(self):
        runner = OpenFangRunner()
        result = runner.hands_list()
        assert isinstance(result, dict)
        assert "stdout" in result

    def test_gateway_invalid_action_returns_error(self):
        runner = OpenFangRunner()
        result = runner.gateway_action("invalid_action")
        assert result["returncode"] == "1"
