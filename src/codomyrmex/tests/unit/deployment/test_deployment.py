"""Unit tests for deployment module."""

import pytest
from unittest.mock import MagicMock, patch
from codomyrmex.deployment import DeploymentManager, CanaryStrategy, BlueGreenStrategy, GitOpsSynchronizer

@pytest.mark.unit
def test_canary_deployment():
    """Test Canary strategy execution via manager."""
    manager = DeploymentManager()
    # Use stage_duration_seconds=0 to avoid time.sleep() delays
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
    """Test manager handling of strategy failures."""
    manager = DeploymentManager()
    mock_strategy = MagicMock()
    mock_strategy.deploy.side_effect = Exception("System down")

    result = manager.deploy("failing-service", "v1", mock_strategy)
    assert result is False

@pytest.mark.unit
def test_gitops_sync():
    """Test GitOpsSynchronizer logic."""
    with patch('subprocess.run') as mock_run:
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "abc1234\n"
        mock_run.return_value = mock_result

        sync = GitOpsSynchronizer("https://github.com/org/repo", "/tmp/claude/repo")

        version = sync.get_version()
        assert version == "abc1234"
