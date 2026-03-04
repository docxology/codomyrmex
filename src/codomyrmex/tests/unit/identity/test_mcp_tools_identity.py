"""Tests for identity MCP tools.

Zero-mock tests validating the identity MCP tool wrappers.
"""

from __future__ import annotations


class TestIdentityListLevels:
    """Tests for identity_list_levels tool."""

    def test_returns_success_status(self):
        from codomyrmex.identity.mcp_tools import identity_list_levels

        result = identity_list_levels()
        assert result["status"] == "success"

    def test_contains_all_levels(self):
        from codomyrmex.identity.mcp_tools import identity_list_levels

        result = identity_list_levels()
        values = [lv["value"] for lv in result["levels"]]
        assert "unverified" in values
        assert "kyc_verified" in values

    def test_level_entries_have_name_and_value(self):
        from codomyrmex.identity.mcp_tools import identity_list_levels

        result = identity_list_levels()
        for level in result["levels"]:
            assert "name" in level
            assert "value" in level


class TestIdentityCreatePersona:
    """Tests for identity_create_persona tool."""

    def test_create_basic_persona(self):
        from codomyrmex.identity.mcp_tools import identity_create_persona

        result = identity_create_persona(
            persona_id="test-001",
            name="Test User",
        )
        assert result["status"] == "success"
        assert result["persona"]["id"] == "test-001"
        assert result["persona"]["name"] == "Test User"
        assert result["persona"]["level"] == "unverified"

    def test_create_persona_with_level(self):
        from codomyrmex.identity.mcp_tools import identity_create_persona

        result = identity_create_persona(
            persona_id="verified-001",
            name="Verified User",
            level="kyc_verified",
        )
        assert result["status"] == "success"
        assert result["persona"]["level"] == "kyc_verified"

    def test_create_persona_with_capabilities(self):
        from codomyrmex.identity.mcp_tools import identity_create_persona

        result = identity_create_persona(
            persona_id="cap-001",
            name="Capable User",
            capabilities=["read", "write", "admin"],
        )
        assert result["status"] == "success"
        assert result["persona"]["capabilities"] == ["read", "write", "admin"]

    def test_invalid_level_returns_error(self):
        from codomyrmex.identity.mcp_tools import identity_create_persona

        result = identity_create_persona(
            persona_id="bad-001",
            name="Bad Level",
            level="fake_level",
        )
        assert result["status"] == "error"
        assert "message" in result


class TestIdentityCheckCapability:
    """Tests for identity_check_capability tool."""

    def test_has_capability(self):
        from codomyrmex.identity.mcp_tools import identity_check_capability

        result = identity_check_capability(
            capabilities=["read", "write", "admin"],
            required_capability="write",
        )
        assert result["status"] == "success"
        assert result["has_capability"] is True

    def test_missing_capability(self):
        from codomyrmex.identity.mcp_tools import identity_check_capability

        result = identity_check_capability(
            capabilities=["read"],
            required_capability="admin",
        )
        assert result["status"] == "success"
        assert result["has_capability"] is False

    def test_empty_capabilities(self):
        from codomyrmex.identity.mcp_tools import identity_check_capability

        result = identity_check_capability(
            capabilities=[],
            required_capability="anything",
        )
        assert result["status"] == "success"
        assert result["has_capability"] is False

    def test_returns_required_and_provided(self):
        from codomyrmex.identity.mcp_tools import identity_check_capability

        result = identity_check_capability(
            capabilities=["a", "b"],
            required_capability="a",
        )
        assert result["required"] == "a"
        assert result["provided"] == ["a", "b"]
