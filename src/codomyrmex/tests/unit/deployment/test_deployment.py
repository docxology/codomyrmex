"""Zero-Mock tests for deployment module.

Uses real strategy objects and real subprocess for GitOps tests.
"""

import subprocess

import pytest

from codomyrmex.deployment import (
    BlueGreenStrategy,
    CanaryStrategy,
    DeploymentManager,
    GitOpsSynchronizer,
)


@pytest.mark.unit
def test_canary_deployment():
    """Test Canary strategy execution via manager."""
    manager = DeploymentManager()
    strategy = CanaryStrategy(stages=[15, 30, 50, 100], stage_duration_seconds=0)

    result = manager.deploy("test-service", "v1", strategy)
    assert result is True


@pytest.mark.unit
def test_blue_green_deployment():
    """Test Blue-Green strategy execution via manager."""
    manager = DeploymentManager()
    strategy = BlueGreenStrategy()

    result = manager.deploy("api-server", "v2", strategy)
    assert result is True


@pytest.mark.unit
def test_deployment_failure():
    """Test manager handling of strategy failures using a real failing strategy."""

    class FailingStrategy:
        """A real strategy that always raises."""
        def deploy(self, service_name: str, version: str) -> bool:
            raise RuntimeError("System down")

    manager = DeploymentManager()
    result = manager.deploy("failing-service", "v1", FailingStrategy())
    assert result is False


@pytest.mark.unit
def test_gitops_sync(tmp_path):
    """Test GitOpsSynchronizer with a real git repo."""
    repo_dir = tmp_path / "repo"
    repo_dir.mkdir()

    # Initialize a real git repo
    subprocess.run(["git", "init"], cwd=str(repo_dir), capture_output=True, check=True)
    subprocess.run(
        ["git", "config", "user.email", "test@test.com"],
        cwd=str(repo_dir), capture_output=True, check=True,
    )
    subprocess.run(
        ["git", "config", "user.name", "Test"],
        cwd=str(repo_dir), capture_output=True, check=True,
    )

    # Create a commit
    (repo_dir / "README.md").write_text("# Test")
    subprocess.run(["git", "add", "."], cwd=str(repo_dir), capture_output=True, check=True)
    subprocess.run(
        ["git", "commit", "-m", "init"],
        cwd=str(repo_dir), capture_output=True, check=True,
    )

    sync = GitOpsSynchronizer(str(repo_dir), str(repo_dir))
    version = sync.get_version()

    # Should return a valid git commit hash (7+ hex chars)
    assert version is not None
    assert len(version) >= 7
