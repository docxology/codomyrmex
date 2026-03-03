"""Unit tests for feature store MCP tools."""

import pytest

from codomyrmex.feature_store.mcp_tools import (
    fs_get_features,
    fs_ingest_features,
    fs_list_features,
    fs_list_groups,
)


@pytest.mark.unit
class TestFeatureStoreMCPTools:
    """Test suite for feature store MCP tools."""

    def test_fs_list_groups(self):
        """Verify fs_list_groups returns correct initial groups."""
        groups = fs_list_groups()
        assert isinstance(groups, list)
        assert "user_profile" in groups

    def test_fs_list_features(self):
        """Verify fs_list_features returns registered features."""
        # List all features
        features = fs_list_features()
        assert isinstance(features, list)
        assert len(features) >= 3

        feature_names = [f["name"] for f in features]
        assert "user_age" in feature_names
        assert "user_segment" in feature_names
        assert "is_active" in feature_names

        # List features by group
        group_features = fs_list_features("user_profile")
        assert len(group_features) == 3
        group_feature_names = [f["name"] for f in group_features]
        assert "user_age" in group_feature_names

        # Invalid group returns empty list
        empty = fs_list_features("invalid_group")
        assert empty == []

    def test_fs_ingest_and_get_features(self):
        """Verify fs_ingest_features and fs_get_features functionality."""
        entity_id = "test_user_123"
        features_to_ingest = {
            "user_age": 30,
            "user_segment": "premium",
            "is_active": True,
        }

        # Test valid ingestion
        result = fs_ingest_features(entity_id, features_to_ingest)
        assert "Successfully ingested" in result
        assert "3" in result

        # Test retrieval by feature names
        retrieved_names = fs_get_features(entity_id, feature_names=["user_age", "is_active"])
        assert retrieved_names == {"user_age": 30, "is_active": True}

        # Test retrieval by group
        retrieved_group = fs_get_features(entity_id, group_name="user_profile")
        assert retrieved_group == {"user_age": 30, "user_segment": "premium", "is_active": True}

        # Test retrieval of all features (fallback when no names/group provided)
        retrieved_all = fs_get_features(entity_id)
        assert retrieved_all["user_age"] == 30
        assert retrieved_all["user_segment"] == "premium"

    def test_fs_ingest_features_errors(self):
        """Verify error handling in fs_ingest_features."""
        entity_id = "test_user_456"

        # Test unregistered feature
        result_not_found = fs_ingest_features(entity_id, {"unregistered_feature": 10})
        assert "Error: Feature not found" in result_not_found

        # Test validation error (wrong type)
        result_validation = fs_ingest_features(entity_id, {"user_age": "thirty"})
        assert "Error: Validation failed" in result_validation

    def test_tool_metadata(self):
        """Verify tools have the correct MCP metadata."""
        assert getattr(fs_list_groups, "_mcp_tool_meta", None) is not None
        assert fs_list_groups._mcp_tool_meta["name"] == "codomyrmex.fs_list_groups"
        assert fs_list_groups._mcp_tool_meta["category"] == "Feature Store"

        assert getattr(fs_list_features, "_mcp_tool_meta", None) is not None
        assert getattr(fs_get_features, "_mcp_tool_meta", None) is not None
        assert getattr(fs_ingest_features, "_mcp_tool_meta", None) is not None
