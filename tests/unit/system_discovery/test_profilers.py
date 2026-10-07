import os
import platform
import sys
from pathlib import Path

import pytest

from codomyrmex.system_discovery.reporting.profilers import (
    EnvironmentProfiler,
    HardwareProfiler,
)


def create_fake_executable(
    base_path: Path, name: str, output: str = "", fail: bool = False
) -> None:
    """Create a cross-platform fake executable for testing."""
    # Unix script
    sh_path = base_path / name
    if fail:
        sh_path.write_text("#!/bin/sh\nexit 1\n")
    else:
        sh_path.write_text(f"#!/bin/sh\ncat << 'EOF'\n{output}\nEOF\n")
    sh_path.chmod(0o755)

    # Windows bat
    bat_path = base_path / f"{name}.bat"
    if fail:
        bat_path.write_text("@echo off\nexit /b 1\n")
    else:
        lines = [f"echo {line}" for line in output.split("\n") if line]
        bat_content = "@echo off\n" + "\n".join(lines) + "\n"
        bat_path.write_text(bat_content)


def test_gpu_info_nvidia_smi(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """Test get_gpu_info when nvidia-smi is available in PATH."""
    fake_bin = tmp_path / "bin"
    fake_bin.mkdir()

    output = "GeForce RTX 3090, 24576, 510.39.01\nTesla T4, 15360, 510.39.01"
    create_fake_executable(fake_bin, "nvidia-smi", output)

    old_path = os.environ.get("PATH", "")
    monkeypatch.setenv("PATH", f"{fake_bin}{os.pathsep}{old_path}")

    gpu_info = HardwareProfiler.get_gpu_info()

    assert gpu_info["available"] is True

    found_3090 = False
    found_t4 = False
    for detail in gpu_info["details"]:
        if detail.get("vendor") == "NVIDIA":
            if detail.get("model") == "GeForce RTX 3090":
                assert detail["memory_mb"] == 24576.0
                assert detail["driver_version"] == "510.39.01"
                found_3090 = True
            elif detail.get("model") == "Tesla T4":
                assert detail["memory_mb"] == 15360.0
                assert detail["driver_version"] == "510.39.01"
                found_t4 = True

    assert found_3090
    assert found_t4


def test_gpu_info_rocm_smi(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """Test get_gpu_info when rocm-smi is available in PATH."""
    fake_bin = tmp_path / "bin"
    fake_bin.mkdir()

    create_fake_executable(fake_bin, "rocm-smi", "rocm-smi")
    monkeypatch.setenv("PATH", str(fake_bin))

    gpu_info = HardwareProfiler.get_gpu_info()

    assert gpu_info["available"] is True

    found_amd = False
    for detail in gpu_info["details"]:
        if detail.get("vendor") == "AMD":
            assert detail.get("tool") == "rocm-smi detected"
            found_amd = True

    assert found_amd


def test_gpu_info_nvidia_smi_failure(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """Test get_gpu_info handles nvidia-smi execution failure gracefully."""
    fake_bin = tmp_path / "bin"
    fake_bin.mkdir()

    create_fake_executable(fake_bin, "nvidia-smi", fail=True)
    monkeypatch.setenv("PATH", str(fake_bin))

    gpu_info = HardwareProfiler.get_gpu_info()
    nvidia_details = [d for d in gpu_info["details"] if d.get("vendor") == "NVIDIA"]
    assert len(nvidia_details) == 0


def test_gpu_info_nvidia_smi_malformed(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """Test get_gpu_info handles malformed nvidia-smi output gracefully."""
    fake_bin = tmp_path / "bin"
    fake_bin.mkdir()

    create_fake_executable(fake_bin, "nvidia-smi", "GeForce RTX 3090, 24576")
    monkeypatch.setenv("PATH", str(fake_bin))

    gpu_info = HardwareProfiler.get_gpu_info()
    nvidia_details = [d for d in gpu_info["details"] if d.get("vendor") == "NVIDIA"]
    assert len(nvidia_details) == 0


def test_gpu_info_system_profiler(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """Test get_gpu_info parses system_profiler output correctly on macOS."""
    monkeypatch.setattr(platform, "system", lambda: "Darwin")

    fake_bin = tmp_path / "bin"
    fake_bin.mkdir()

    output = "Chipset Model: Apple M2 Max\nChipset Model: Apple M1"
    create_fake_executable(fake_bin, "system_profiler", output)

    old_path = os.environ.get("PATH", "")
    monkeypatch.setenv("PATH", f"{fake_bin}{os.pathsep}{old_path}")

    gpu_info = HardwareProfiler.get_gpu_info()

    assert gpu_info["available"] is True, f"gpu_info is {gpu_info}"

    found_m2 = False
    found_m1 = False
    for detail in gpu_info["details"]:
        if detail.get("vendor") == "Apple/Other":
            if detail.get("model") == "Apple M2 Max":
                found_m2 = True
            elif detail.get("model") == "Apple M1":
                found_m1 = True

    assert found_m2
    assert found_m1


def test_gpu_info_no_gpu(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """Test get_gpu_info when no GPU tools are available on non-Darwin systems."""
    monkeypatch.setattr(platform, "system", lambda: "Linux")
    fake_bin = tmp_path / "bin"
    fake_bin.mkdir()

    monkeypatch.setenv("PATH", str(fake_bin))

    gpu_info = HardwareProfiler.get_gpu_info()

    assert gpu_info["available"] is False
    assert len(gpu_info["details"]) == 0


def test_is_virtual_env_real_prefix(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test is_virtual_env when sys.real_prefix is set."""
    monkeypatch.setattr(sys, "real_prefix", "/usr", raising=False)
    assert EnvironmentProfiler.is_virtual_env() is True


def test_is_virtual_env_base_prefix_differs(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test is_virtual_env when sys.base_prefix differs from sys.prefix."""
    monkeypatch.delattr(sys, "real_prefix", raising=False)
    monkeypatch.setattr(sys, "base_prefix", "/usr")
    monkeypatch.setattr(sys, "prefix", "/usr/local")
    monkeypatch.delenv("VIRTUAL_ENV", raising=False)
    assert EnvironmentProfiler.is_virtual_env() is True


def test_is_virtual_env_env_var(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test is_virtual_env when VIRTUAL_ENV is set."""
    monkeypatch.delattr(sys, "real_prefix", raising=False)
    monkeypatch.setattr(sys, "base_prefix", "/usr")
    monkeypatch.setattr(sys, "prefix", "/usr")
    monkeypatch.setenv("VIRTUAL_ENV", "/venv")
    assert EnvironmentProfiler.is_virtual_env() is True


def test_is_virtual_env_false(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test is_virtual_env when not in a virtual environment."""
    monkeypatch.delattr(sys, "real_prefix", raising=False)
    monkeypatch.setattr(sys, "base_prefix", "/usr")
    monkeypatch.setattr(sys, "prefix", "/usr")
    monkeypatch.delenv("VIRTUAL_ENV", raising=False)
    assert EnvironmentProfiler.is_virtual_env() is False


@pytest.mark.parametrize(
    ("env_vars", "path_exists_return", "release_return", "expected_type"),
    [
        ({"GITHUB_ACTIONS": "true"}, False, "generic", "ci_github"),
        ({"TRAVIS": "true"}, False, "generic", "ci_travis"),
        ({"CIRCLECI": "true"}, False, "generic", "ci_circleci"),
        ({}, True, "generic", "docker"),  # docker path exists
        ({"KUBERNETES_SERVICE_HOST": "10.0.0.1"}, False, "generic", "kubernetes"),
        ({"WSL_DISTRO_NAME": "Ubuntu"}, False, "generic", "wsl"),
        ({}, False, "5.15.90.1-microsoft-standard-WSL2", "wsl"),
        ({}, False, "generic", "local"),
    ],
)
def test_get_environment_type(
    monkeypatch: pytest.MonkeyPatch,
    env_vars: dict[str, str],
    path_exists_return: bool,
    release_return: str,
    expected_type: str,
) -> None:
    """Test get_environment_type detects environment correctly."""
    # Mock environment variables
    monkeypatch.setattr(os, "environ", env_vars)

    # Mock os.path.exists
    original_exists = os.path.exists

    def mock_exists(path: str) -> bool:
        if path == "/.dockerenv":
            return path_exists_return
        return original_exists(path)

    monkeypatch.setattr(os.path, "exists", mock_exists)

    # Mock platform.release
    monkeypatch.setattr(platform, "release", lambda: release_return)

    assert EnvironmentProfiler.get_environment_type() == expected_type


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


@pytest.mark.unit
class TestHardwareProfiler:
    """Tests for HardwareProfiler."""

    def test_get_hardware_info(self):
        """Test getting hardware info returns expected keys and types."""
        info = HardwareProfiler.get_hardware_info()

        # Should be a dictionary
        assert isinstance(info, dict)

        # Base keys
        assert "cpu_count" in info
        assert "cpu_threads" in info
        assert "os" in info
        assert "os_release" in info
        assert "os_version" in info
        assert "architecture" in info
        assert "processor" in info
        assert "gpu" in info

        # Optional keys based on psutil availability
        assert "cpu_freq" in info
        assert "total_ram_gb" in info
        assert "available_ram_gb" in info

        # Type checks
        assert isinstance(info["cpu_count"], (int, type(None)))
        assert isinstance(info["cpu_threads"], (int, type(None)))
        assert isinstance(info["os"], str)
        assert isinstance(info["os_release"], str)
        assert isinstance(info["os_version"], str)
        assert isinstance(info["architecture"], str)
        assert isinstance(info["processor"], str)
        assert isinstance(info["gpu"], dict)
        assert "available" in info["gpu"]
        assert "details" in info["gpu"]

        assert isinstance(info["cpu_freq"], (dict, type(None)))
        assert isinstance(info["total_ram_gb"], (float, int, type(None)))
        assert isinstance(info["available_ram_gb"], (float, int, type(None)))
