"""Tests for feature_store MCP tools.

Zero-mock tests validating the feature_store MCP tool wrappers.
"""

from __future__ import annotations


class TestFeatureStoreListTypes:
    """Tests for feature_store_list_types tool."""

    def test_returns_success_status(self):
        from codomyrmex.feature_store.mcp_tools import feature_store_list_types

        result = feature_store_list_types()
        assert result["status"] == "success"

    def test_contains_feature_types(self):
        from codomyrmex.feature_store.mcp_tools import feature_store_list_types

        result = feature_store_list_types()
        assert "feature_types" in result
        assert "numeric" in result["feature_types"]
        assert "categorical" in result["feature_types"]

    def test_contains_value_types(self):
        from codomyrmex.feature_store.mcp_tools import feature_store_list_types

        result = feature_store_list_types()
        assert "value_types" in result
        assert "int" in result["value_types"]
        assert "float" in result["value_types"]
        assert "string" in result["value_types"]


class TestFeatureStoreRegisterFeature:
    """Tests for feature_store_register_feature tool."""

    def test_register_numeric_feature(self):
        from codomyrmex.feature_store.mcp_tools import feature_store_register_feature

        result = feature_store_register_feature(
            name="user_age",
            feature_type="numeric",
            value_type="int",
            description="Age of the user",
        )
        assert result["status"] == "success"
        assert result["feature"]["name"] == "user_age"
        assert result["feature"]["feature_type"] == "numeric"
        assert result["feature"]["value_type"] == "int"

    def test_register_categorical_feature(self):
        from codomyrmex.feature_store.mcp_tools import feature_store_register_feature

        result = feature_store_register_feature(
            name="user_city",
            feature_type="categorical",
            value_type="string",
        )
        assert result["status"] == "success"
        assert result["feature"]["feature_type"] == "categorical"

    def test_invalid_feature_type_returns_error(self):
        from codomyrmex.feature_store.mcp_tools import feature_store_register_feature

        result = feature_store_register_feature(
            name="bad",
            feature_type="nonexistent_type",
            value_type="int",
        )
        assert result["status"] == "error"
        assert "message" in result


class TestFeatureStoreValidateValue:
    """Tests for feature_store_validate_value tool."""

    def test_valid_int_value(self):
        from codomyrmex.feature_store.mcp_tools import feature_store_validate_value

        result = feature_store_validate_value(value=42, value_type="int")
        assert result["status"] == "success"
        assert result["valid"] is True

    def test_invalid_int_value(self):
        from codomyrmex.feature_store.mcp_tools import feature_store_validate_value

        result = feature_store_validate_value(value="not_an_int", value_type="int")
        assert result["status"] == "success"
        assert result["valid"] is False

    def test_none_value_is_valid(self):
        from codomyrmex.feature_store.mcp_tools import feature_store_validate_value

        result = feature_store_validate_value(value=None, value_type="float")
        assert result["status"] == "success"
        assert result["valid"] is True

    def test_invalid_value_type_returns_error(self):
        from codomyrmex.feature_store.mcp_tools import feature_store_validate_value

        result = feature_store_validate_value(value=1, value_type="nonexistent")
        assert result["status"] == "error"
