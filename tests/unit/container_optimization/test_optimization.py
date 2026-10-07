import contextlib
import os
import shutil
import subprocess
import time

import pytest

pytest.importorskip(
    "docker.errors",
    reason="container optimization tests require docker SDK (uv sync --extra containerization)",
)
import docker
from docker import errors as docker_errors

from codomyrmex.container_optimization.optimizer import ContainerOptimizer
from codomyrmex.container_optimization.resource_tuner import (
    ResourceTuner,
    ResourceUsage,
)


@pytest.fixture(scope="session")
def docker_client():
    """Provides a Docker client for tests."""
    docker_path = shutil.which("docker")
    if docker_path is None:
        pytest.skip("Docker CLI is not available")
    try:
        probe = subprocess.run(
            [docker_path, "info", "--format", "{{.ServerVersion}}"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if probe.returncode != 0 or not probe.stdout.strip():
            pytest.skip("Docker daemon unavailable")
        client = docker.from_env(version=os.environ.get("DOCKER_API_VERSION", "1.41"))
        client.ping()
    except (OSError, subprocess.TimeoutExpired, docker_errors.DockerException) as exc:
        if "client" in locals():
            client.close()
        pytest.skip(f"Docker daemon unavailable: {exc}")
    try:
        yield client
    finally:
        client.close()


@pytest.fixture(scope="module")
def existing_image(docker_client):
    """Uses an existing image to avoid build issues in restricted environments."""
    images = docker_client.images.list()
    if not images:
        pytest.skip("No Docker images available for testing")
    # Prefer non-sha256 tags if possible for better test visibility
    for img in images:
        if img.tags:
            return img.tags[0]
    return images[0].id


# Images known to ship a ``sleep`` binary; CI pulls python:3.9-slim and bash:5.1.
_SLEEP_CAPABLE = ("python:", "bash:", "alpine", "busybox", "ubuntu", "debian")


@pytest.fixture(scope="module")
def running_container(docker_client, existing_image):
    """Runs a long-lived container for testing resource tuning.

    Regression: the first tagged image was used blindly. When its entrypoint
    could not run ``sleep`` the container exited at once and was auto-removed,
    so ``stats()`` returned an empty body (JSONDecodeError) instead of the test
    skipping. Prefer images that have ``sleep`` and require a running state.
    """
    tags = [tag for image in docker_client.images.list() for tag in image.tags]
    image = next(
        (tag for tag in tags if tag.startswith(_SLEEP_CAPABLE)), existing_image
    )
    try:
        container = docker_client.containers.run(
            image, command=["sleep", "100"], entrypoint="", detach=True, remove=True
        )
    except docker_errors.DockerException as exc:
        pytest.skip(f"Could not run container {image!r}: {exc}")
    try:
        deadline = time.monotonic() + 10
        while time.monotonic() < deadline:
            try:
                container.reload()
            except docker_errors.NotFound:
                pytest.skip(f"Container from {image!r} exited immediately")
            if container.status == "running":
                break
            time.sleep(0.2)
        else:
            pytest.skip(f"Container from {image!r} did not stay running")
        yield container
    finally:
        with contextlib.suppress(docker_errors.DockerException):
            container.stop(timeout=1)


class TestContainerOptimizer:
    """Zero-mock tests for ContainerOptimizer."""

    def test_analyze_image(self, existing_image):
        optimizer = ContainerOptimizer()
        analysis = optimizer.analyze_image(existing_image)

        assert analysis.image_name == existing_image
        assert analysis.size_bytes >= 0
        assert isinstance(analysis.base_image, str)

    def test_suggest_optimizations(self, existing_image):
        optimizer = ContainerOptimizer()
        suggestions = optimizer.suggest_optimizations(existing_image)
        assert isinstance(suggestions, list)

    def test_get_optimization_report(self, existing_image):
        optimizer = ContainerOptimizer()
        report = optimizer.get_optimization_report(existing_image)

        assert "analysis" in report
        assert "suggestions" in report
        assert "score" in report


class TestResourceTuner:
    """Zero-mock tests for ResourceTuner."""

    def test_analyze_usage_real(self, running_container):
        tuner = ResourceTuner()
        time.sleep(1)  # Wait for stats to be available
        usage = tuner.analyze_usage(running_container.id)
        assert isinstance(usage, ResourceUsage)
        assert usage.container_id == running_container.id
        assert usage.memory_usage_bytes > 0

    def test_suggest_limits_basic(self):
        tuner = ResourceTuner()
        usage = ResourceUsage(
            container_id="test",
            cpu_percent=5.0,
            memory_usage_bytes=100 * 1024 * 1024,
            memory_limit_bytes=512 * 1024 * 1024,
            memory_percent=20.0,
        )
        suggestions = tuner.suggest_limits(usage)
        assert suggestions["cpu_limit"] == "0.5"
        assert suggestions["memory_limit"] == "120m"
