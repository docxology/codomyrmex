"""Unit tests for feature_store MCP tools."""

import pytest

from codomyrmex.feature_store.mcp_tools import (
    feature_store_get_features,
    feature_store_ingest,
    feature_store_register_feature,
    get_mcp_tools,
)


@pytest.mark.unit
def test_get_mcp_tools():
    """Verify get_mcp_tools returns expected tools."""
    tools = get_mcp_tools()
    assert isinstance(tools, list)
    assert feature_store_register_feature in tools
    assert feature_store_ingest in tools
    assert feature_store_get_features in tools


@pytest.mark.unit
def test_feature_store_register_feature():
    """Verify feature_store_register_feature registers a feature definition."""
    result = feature_store_register_feature(
        name="test_user_age",
        feature_type="numeric",
        value_type="int",
        description="User age in years",
        default_value=0,
    )

    assert result["status"] == "success"
    assert "test_user_age" in result["message"]

    definition = result["feature"]
    assert definition["name"] == "test_user_age"
    assert definition["feature_type"] == "numeric"
    assert definition["value_type"] == "int"
    assert definition["description"] == "User age in years"
    assert definition["default_value"] == 0


@pytest.mark.unit
def test_feature_store_register_feature_invalid_type():
    """Verify feature_store_register_feature returns error dict for invalid types."""
    result = feature_store_register_feature(
        name="test_invalid",
        feature_type="invalid_type",
        value_type="int",
    )
    assert result["status"] == "error"
    assert "Invalid feature type" in result["message"]

    result2 = feature_store_register_feature(
        name="test_invalid",
        feature_type="numeric",
        value_type="invalid_type",
    )
    assert result2["status"] == "error"
    assert "Invalid value type" in result2["message"]


@pytest.mark.unit
def test_feature_store_ingest_and_get():
    """Verify feature_store_ingest stores values and feature_store_get_features retrieves them."""
    # Register features
    feature_store_register_feature(
        name="user_score",
        feature_type="numeric",
        value_type="float",
        default_value=0.0,
    )
    feature_store_register_feature(
        name="user_role",
        feature_type="categorical",
        value_type="string",
    )

    # Ingest features
    ingest_result = feature_store_ingest(
        entity_id="user_999",
        features={
            "user_score": 95.5,
            "user_role": "admin",
        },
    )

    assert ingest_result["status"] == "success"
    assert ingest_result["features"] == {"user_score": 95.5, "user_role": "admin"}

    # Get features
    get_result = feature_store_get_features(
        entity_id="user_999",
        feature_names=["user_score", "user_role", "user_unknown"],
    )

    assert get_result["status"] == "success"
    assert get_result["entity_id"] == "user_999"
    assert get_result["features"]["user_score"] == 95.5
    assert get_result["features"]["user_role"] == "admin"
    assert get_result["features"].get("user_unknown") is None
    assert "timestamp" in get_result


@pytest.mark.unit
def test_feature_store_ingest_invalid():
    """Verify feature_store_ingest handles errors when ingesting invalid features."""
    from codomyrmex.feature_store.exceptions import FeatureNotFoundError

    with pytest.raises(FeatureNotFoundError):
        feature_store_ingest(
            entity_id="user_err",
            features={"completely_unknown_feature": 123},
        )
