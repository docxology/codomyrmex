"""Unit tests for feature_flags module."""

import pytest
from codomyrmex.feature_flags import FeatureManager

def test_static_flags():
    """Test simple boolean flags."""
    config = {"feature-a": True, "feature-b": False}
    manager = FeatureManager(config)
    
    assert manager.is_enabled("feature-a") is True
    assert manager.is_enabled("feature-b") is False
    assert manager.is_enabled("missing", default=True) is True

def test_percentage_rollout():
    """Test percentage-based rollout logic."""
    config = {"new-feature": {"percentage": 50}}
    manager = FeatureManager(config)
    
    # We should get deterministic results for the same user_id
    res1 = manager.is_enabled("new-feature", user_id="user_1")
    res1_bis = manager.is_enabled("new-feature", user_id="user_1")
    assert res1 == res1_bis
    
    # Test multiple users to see distribution
    enabled_count = 0
    for i in range(100):
        if manager.is_enabled("new-feature", user_id=f"user_{i}"):
            enabled_count += 1
    
    # with 100 users and 50% rollout, we expect roughly 50 (deterministic so testable)
    # The actual count depends on hash(f"new-feature:user_{i}") % 100
    assert enabled_count > 0 and enabled_count < 100

def test_multivariate_flags():
    """Test non-boolean flags."""
    config = {"theme": "dark", "max-connections": 10}
    manager = FeatureManager(config)
    
    assert manager.get_value("theme") == "dark"
    assert manager.get_value("max-connections") == 10
    assert manager.get_value("missing", default="blue") == "blue"

def test_flag_persistence(tmp_path):
    """Test loading and saving flags."""
    file_path = str(tmp_path / "flags.json")
    manager = FeatureManager({"feat-c": True})
    manager.save_to_file(file_path)
    
    new_manager = FeatureManager()
    new_manager.load_from_file(file_path)
    assert new_manager.is_enabled("feat-c") is True
