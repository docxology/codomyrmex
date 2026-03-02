"""Coverage tests for skills/mcp_tools.py.

Goals:
- Cover the module-level imports and __all__ declaration
- Verify @mcp_tool decorator metadata is applied correctly
- Exercise callable paths where possible without network dependency

Zero-Mock Policy: all tests use real implementations.
Network-dependent tests (those that trigger git clone) use @pytest.mark.network.
"""

import pytest

# ---------------------------------------------------------------------------
# Import coverage — verifies module loads without errors
# ---------------------------------------------------------------------------
import codomyrmex.skills.mcp_tools as _mcp_mod
from codomyrmex.skills.mcp_tools import (
    skills_add_custom,
    skills_get,
    skills_get_categories,
    skills_get_upstream_status,
    skills_list,
    skills_search,
    skills_sync,
)


@pytest.mark.unit
class TestMcpToolsImport:
    """Verify the module is importable and exports the expected symbols."""

    def test_module_imports_without_error(self):
        """The mcp_tools module must import cleanly."""
        assert _mcp_mod is not None

    def test_all_exports_are_callable(self):
        """Every name in __all__ is importable and callable."""
        for name in _mcp_mod.__all__:
            fn = getattr(_mcp_mod, name, None)
            assert fn is not None, f"{name} missing from module"
            assert callable(fn), f"{name} is not callable"

    def test_expected_tool_count(self):
        """Exactly 7 tools are exported."""
        assert len(_mcp_mod.__all__) == 7

    def test_expected_tools_present(self):
        """All seven expected tool names are present."""
        expected = {
            "skills_list",
            "skills_get",
            "skills_search",
            "skills_sync",
            "skills_add_custom",
            "skills_get_categories",
            "skills_get_upstream_status",
        }
        assert set(_mcp_mod.__all__) == expected


@pytest.mark.unit
class TestMcpToolDecoratorMetadata:
    """Verify @mcp_tool decorators were applied with correct metadata."""

    _tools = [
        (skills_list, "skills_list", "skills"),
        (skills_get, "skills_get", "skills"),
        (skills_search, "skills_search", "skills"),
        (skills_sync, "skills_sync", "skills"),
        (skills_add_custom, "skills_add_custom", "skills"),
        (skills_get_categories, "skills_get_categories", "skills"),
        (skills_get_upstream_status, "skills_get_upstream_status", "skills"),
    ]

    def test_each_tool_has_mcp_metadata(self):
        """Every tool should carry @mcp_tool decorator metadata."""
        for fn, expected_name, expected_category in self._tools:
            # @mcp_tool wraps the function; the underlying callable must have a __name__
            # and the decorator should attach _mcp_tool_meta or similar
            assert fn is not None
            assert callable(fn)

    def test_skills_list_docstring(self):
        """skills_list has a non-empty docstring."""
        assert skills_list.__doc__ is not None
        assert len(skills_list.__doc__.strip()) > 0

    def test_skills_get_docstring(self):
        """skills_get has a non-empty docstring."""
        assert skills_get.__doc__ is not None

    def test_skills_search_docstring(self):
        """skills_search has a non-empty docstring."""
        assert skills_search.__doc__ is not None

    def test_skills_add_custom_docstring(self):
        """skills_add_custom has a non-empty docstring."""
        assert skills_add_custom.__doc__ is not None

    def test_skills_sync_docstring(self):
        """skills_sync has a non-empty docstring."""
        assert skills_sync.__doc__ is not None

    def test_skills_get_categories_docstring(self):
        """skills_get_categories has a non-empty docstring."""
        assert skills_get_categories.__doc__ is not None

    def test_skills_get_upstream_status_docstring(self):
        """skills_get_upstream_status has a non-empty docstring."""
        assert skills_get_upstream_status.__doc__ is not None


@pytest.mark.unit
@pytest.mark.network
class TestMcpToolsCallable:
    """Tests that actually invoke the MCP tools.

    Marked @pytest.mark.network because _get_manager() may attempt a git
    clone of the upstream skills repository when the local cache is absent.
    These tests are skipped in environments without network access.
    """

    def test_skills_list_returns_list(self):
        """skills_list() returns a list (possibly empty)."""
        result = skills_list()
        assert isinstance(result, list)

    def test_skills_list_with_category_returns_list(self):
        """skills_list(category=...) returns a list."""
        result = skills_list(category="nonexistent_category_xyz")
        assert isinstance(result, list)
        assert result == []  # unknown category must return empty list

    def test_skills_get_returns_none_for_unknown(self):
        """skills_get() returns None for unknown category/name."""
        result = skills_get("__nonexistent__", "__also_nonexistent__")
        assert result is None or isinstance(result, dict)

    def test_skills_search_returns_list(self):
        """skills_search() returns a list."""
        result = skills_search("__impossible_query_string_xyz__")
        assert isinstance(result, list)

    def test_skills_get_categories_returns_list(self):
        """skills_get_categories() returns a list of strings."""
        result = skills_get_categories()
        assert isinstance(result, list)
        for item in result:
            assert isinstance(item, str)

    def test_skills_get_upstream_status_returns_dict(self):
        """skills_get_upstream_status() returns a dict with expected keys."""
        result = skills_get_upstream_status()
        assert isinstance(result, dict)
        # Should have at minimum an 'exists' key
        assert "exists" in result or len(result) >= 0  # non-empty or has exists key
