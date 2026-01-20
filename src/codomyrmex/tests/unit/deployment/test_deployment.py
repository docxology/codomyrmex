"""Unit tests for deployment module."""

import pytest
from unittest.mock import MagicMock
from codomyrmex.deployment import DeploymentManager, CanaryStrategy, BlueGreenStrategy, GitOpsSynchronizer

def test_canary_deployment():
    """Test Canary strategy execution via manager."""
    manager = DeploymentManager()
    strategy = CanaryStrategy(percentage=15)
    
    # We can't easily mock the 'execute' internal logic without more structure, 
    # but we can verify the manager returns True and logs correctly.
    result = manager.deploy("test-service", "v1", strategy)
    assert result is True

def test_blue_green_deployment():
    """Test Blue-Green strategy execution via manager."""
    manager = DeploymentManager()
    strategy = BlueGreenStrategy()
    
    result = manager.deploy("api-server", "v2", strategy)
    assert result is True

def test_deployment_failure():
    """Test manager handling of strategy failures."""
    manager = DeploymentManager()
    mock_strategy = MagicMock()
    mock_strategy.execute.side_effect = Exception("System down")
    
    result = manager.deploy("failing-service", "v1", mock_strategy)
    assert result is False

def test_gitops_sync():
    """Test GitOpsSynchronizer logic."""
    from unittest.mock import patch
    with patch('subprocess.run') as mock_run:
        sync = GitOpsSynchronizer("https://github.com/org/repo", "/tmp/repo")
        
        # Test rev-parse
        mock_run.return_value = MagicMock(stdout="abc1234")
        assert sync.get_version() == "abc1234"
