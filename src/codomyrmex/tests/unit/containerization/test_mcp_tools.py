import pytest

import codomyrmex.containerization as containerization_pkg
from codomyrmex.containerization.mcp_tools import (
    container_build,
    container_list,
    container_runtime_status,
    container_security_scan,
)


@pytest.mark.unit
def test_container_runtime_status(monkeypatch):
    """Test runtime status report logic without mocking structure."""

    # Since mcp_tools imports these from `.`, they come from `codomyrmex.containerization`
    # We patch them directly on the package module.
    monkeypatch.setattr(containerization_pkg, "HAS_DOCKER_MANAGER", True, raising=False)
    monkeypatch.setattr(containerization_pkg, "HAS_K8S", False, raising=False)
    monkeypatch.setattr(containerization_pkg, "HAS_REGISTRY", True, raising=False)
    monkeypatch.setattr(containerization_pkg, "HAS_SCANNER", False, raising=False)
    monkeypatch.setattr(containerization_pkg, "HAS_OPTIMIZER", True, raising=False)

    result = container_runtime_status()
    assert result["status"] == "ok"
    runtimes = result["runtimes"]
    assert runtimes["docker"] is True
    assert runtimes["kubernetes"] is False
    assert runtimes["registry"] is True
    assert runtimes["security_scanner"] is False
    assert runtimes["optimizer"] is True


@pytest.mark.unit
def test_container_build_no_docker_manager(monkeypatch):
    """Test container_build gracefully handles unavailable DockerManager."""
    monkeypatch.setattr(containerization_pkg, "DockerManager", None, raising=False)

    result = container_build("my-image")
    assert result["status"] == "error"
    assert "not available" in result["error"].lower()


@pytest.mark.unit
def test_container_list_no_docker_manager(monkeypatch):
    """Test container_list gracefully handles unavailable DockerManager."""
    monkeypatch.setattr(containerization_pkg, "DockerManager", None, raising=False)

    result = container_list()
    assert result["status"] == "error"
    assert "not available" in result["error"].lower()


@pytest.mark.unit
def test_container_security_scan_no_scanner(monkeypatch):
    """Test container_security_scan gracefully handles unavailable scanner."""
    monkeypatch.setattr(containerization_pkg, "HAS_SCANNER", False, raising=False)
    monkeypatch.setattr(containerization_pkg, "ContainerSecurityScanner", None, raising=False)

    result = container_security_scan("my-image:latest")
    assert result["status"] == "error"
    assert "not available" in result["error"].lower()
