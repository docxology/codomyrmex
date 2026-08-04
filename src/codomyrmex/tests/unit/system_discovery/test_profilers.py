"""Tests for the profilers module."""

import os
import platform

import pytest

from codomyrmex.system_discovery.reporting.profilers import EnvironmentProfiler


@pytest.fixture
def clean_env(monkeypatch: pytest.MonkeyPatch):
    """Fixture to ensure a clean environment for testing."""
    for env_var in [
        "GITHUB_ACTIONS",
        "TRAVIS",
        "CIRCLECI",
        "KUBERNETES_SERVICE_HOST",
        "WSL_DISTRO_NAME",
    ]:
        monkeypatch.delenv(env_var, raising=False)

    original_exists = os.path.exists

    def mock_exists(path):
        if str(path) == "/.dockerenv":
            return False
        return original_exists(path)

    monkeypatch.setattr(os.path, "exists", mock_exists)
    monkeypatch.setattr(platform, "release", lambda: "Generic-OS")


@pytest.mark.unit
class TestEnvironmentProfiler:
    """Test EnvironmentProfiler."""

    def test_get_environment_type_ci_github(
        self, monkeypatch: pytest.MonkeyPatch, clean_env
    ):
        monkeypatch.setenv("GITHUB_ACTIONS", "true")
        assert EnvironmentProfiler.get_environment_type() == "ci_github"

    def test_get_environment_type_ci_travis(
        self, monkeypatch: pytest.MonkeyPatch, clean_env
    ):
        monkeypatch.setenv("TRAVIS", "true")
        assert EnvironmentProfiler.get_environment_type() == "ci_travis"

    def test_get_environment_type_ci_circleci(
        self, monkeypatch: pytest.MonkeyPatch, clean_env
    ):
        monkeypatch.setenv("CIRCLECI", "true")
        assert EnvironmentProfiler.get_environment_type() == "ci_circleci"

    def test_get_environment_type_docker(
        self, monkeypatch: pytest.MonkeyPatch, clean_env
    ):
        original_exists = os.path.exists

        def mock_exists(path):
            if str(path) == "/.dockerenv":
                return True
            return original_exists(path)

        monkeypatch.setattr(os.path, "exists", mock_exists)
        assert EnvironmentProfiler.get_environment_type() == "docker"

    def test_get_environment_type_kubernetes(
        self, monkeypatch: pytest.MonkeyPatch, clean_env
    ):
        monkeypatch.setenv("KUBERNETES_SERVICE_HOST", "true")
        assert EnvironmentProfiler.get_environment_type() == "kubernetes"

    def test_get_environment_type_wsl_env(
        self, monkeypatch: pytest.MonkeyPatch, clean_env
    ):
        monkeypatch.setenv("WSL_DISTRO_NAME", "Ubuntu")
        assert EnvironmentProfiler.get_environment_type() == "wsl"

    def test_get_environment_type_wsl_platform(
        self, monkeypatch: pytest.MonkeyPatch, clean_env
    ):
        monkeypatch.setattr(
            platform, "release", lambda: "5.10.16.3-microsoft-standard-WSL2"
        )
        assert EnvironmentProfiler.get_environment_type() == "wsl"

    def test_get_environment_type_local(self, clean_env):
        assert EnvironmentProfiler.get_environment_type() == "local"
