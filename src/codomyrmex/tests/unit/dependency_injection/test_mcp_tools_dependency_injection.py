"""Tests for dependency_injection MCP tools.

Zero-mock policy: all tests exercise real implementations.
"""

from __future__ import annotations


class TestDependencyInjectionListScopes:
    """Tests for dependency_injection_list_scopes tool."""

    def test_list_scopes_returns_success(self):
        from codomyrmex.dependency_injection.mcp_tools import (
            dependency_injection_list_scopes,
        )

        result = dependency_injection_list_scopes()
        assert result["status"] == "success"
        assert "singleton" in result["scopes"]
        assert "transient" in result["scopes"]
        assert "scoped" in result["scopes"]

    def test_list_scopes_has_descriptions(self):
        from codomyrmex.dependency_injection.mcp_tools import (
            dependency_injection_list_scopes,
        )

        result = dependency_injection_list_scopes()
        assert result["status"] == "success"
        assert "descriptions" in result
        assert "singleton" in result["descriptions"]
        assert "transient" in result["descriptions"]
        assert "scoped" in result["descriptions"]


class TestDependencyInjectionVerifyContainer:
    """Tests for dependency_injection_verify_container tool."""

    def test_verify_container_success(self):
        from codomyrmex.dependency_injection.mcp_tools import (
            dependency_injection_verify_container,
        )

        result = dependency_injection_verify_container()
        assert result["status"] == "success"
        assert result["registration_count"] == 1
        assert result["resolution_ok"] is True

    def test_verify_container_repr(self):
        from codomyrmex.dependency_injection.mcp_tools import (
            dependency_injection_verify_container,
        )

        result = dependency_injection_verify_container()
        assert result["status"] == "success"
        assert "Container" in result["container_repr"]


class TestDependencyInjectionInspectClass:
    """Tests for dependency_injection_inspect_class tool."""

    def test_inspect_non_injectable_class(self):
        from codomyrmex.dependency_injection.mcp_tools import (
            dependency_injection_inspect_class,
        )

        result = dependency_injection_inspect_class(
            class_name="codomyrmex.dependency_injection.container.Container"
        )
        assert result["status"] == "success"
        assert result["is_injectable"] is False

    def test_inspect_invalid_class_name(self):
        from codomyrmex.dependency_injection.mcp_tools import (
            dependency_injection_inspect_class,
        )

        result = dependency_injection_inspect_class(class_name="NoModule")
        assert result["status"] == "error"
        assert "fully qualified" in result["message"]

    def test_inspect_nonexistent_class(self):
        from codomyrmex.dependency_injection.mcp_tools import (
            dependency_injection_inspect_class,
        )

        result = dependency_injection_inspect_class(
            class_name="codomyrmex.dependency_injection.container.NonExistentClass"
        )
        assert result["status"] == "error"
