import os
import platform
from pathlib import Path

import pytest

from codomyrmex.system_discovery.reporting.profilers import HardwareProfiler


def create_fake_executable(base_path: Path, name: str, output: str = "", fail: bool = False) -> None:
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


def test_gpu_info_nvidia_smi_failure(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """Test get_gpu_info handles nvidia-smi execution failure gracefully."""
    fake_bin = tmp_path / "bin"
    fake_bin.mkdir()

    create_fake_executable(fake_bin, "nvidia-smi", fail=True)
    monkeypatch.setenv("PATH", str(fake_bin))

    gpu_info = HardwareProfiler.get_gpu_info()
    nvidia_details = [d for d in gpu_info["details"] if d.get("vendor") == "NVIDIA"]
    assert len(nvidia_details) == 0


def test_gpu_info_nvidia_smi_malformed(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """Test get_gpu_info handles malformed nvidia-smi output gracefully."""
    fake_bin = tmp_path / "bin"
    fake_bin.mkdir()

    create_fake_executable(fake_bin, "nvidia-smi", "GeForce RTX 3090, 24576")
    monkeypatch.setenv("PATH", str(fake_bin))

    gpu_info = HardwareProfiler.get_gpu_info()
    nvidia_details = [d for d in gpu_info["details"] if d.get("vendor") == "NVIDIA"]
    assert len(nvidia_details) == 0


def test_gpu_info_system_profiler(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """Test get_gpu_info parses system_profiler output correctly on macOS."""
    monkeypatch.setattr(platform, "system", lambda: "Darwin")

    fake_bin = tmp_path / "bin"
    fake_bin.mkdir()

    output = "Chipset Model: Apple M2 Max\nChipset Model: Apple M1"
    create_fake_executable(fake_bin, "system_profiler", output)

    monkeypatch.setenv("PATH", str(fake_bin))

    gpu_info = HardwareProfiler.get_gpu_info()

    assert gpu_info["available"] is True

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
