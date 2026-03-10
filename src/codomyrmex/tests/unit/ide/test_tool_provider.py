"""Tests for codomyrmex.ide.antigravity.tool_provider.

Zero-mock compliant — no MagicMock, monkeypatch, or unittest.mock.
Tests exercise the module-level frozensets, static methods, and
AntigravityToolProvider class directly with real instantiation.
"""

from __future__ import annotations

import pytest

from codomyrmex.ide.antigravity.tool_provider import (
    CONTROL_TOOLS,
    DESTRUCTIVE_TOOLS,
    SAFE_TOOLS,
    AntigravityToolProvider,
)

# ---------------------------------------------------------------------------
# SAFE_TOOLS constant
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestSafeToolsConstant:
    """SAFE_TOOLS is a frozenset of read-only tool names."""

    def test_safe_tools_is_frozenset(self):
        """SAFE_TOOLS is a frozenset instance."""
        assert isinstance(SAFE_TOOLS, frozenset)

    def test_safe_tools_count(self):
        """SAFE_TOOLS contains exactly 9 tools."""
        assert len(SAFE_TOOLS) == 9

    def test_view_file_in_safe(self):
        """view_file is classified as safe."""
        assert "view_file" in SAFE_TOOLS

    def test_grep_search_in_safe(self):
        """grep_search is classified as safe."""
        assert "grep_search" in SAFE_TOOLS

    def test_list_dir_in_safe(self):
        """list_dir is classified as safe."""
        assert "list_dir" in SAFE_TOOLS

    def test_command_status_in_safe(self):
        """command_status is classified as safe."""
        assert "command_status" in SAFE_TOOLS

    def test_read_url_content_in_safe(self):
        """read_url_content is classified as safe."""
        assert "read_url_content" in SAFE_TOOLS

    def test_search_web_in_safe(self):
        """search_web is classified as safe."""
        assert "search_web" in SAFE_TOOLS

    def test_safe_tools_immutable(self):
        """SAFE_TOOLS cannot be mutated (frozenset)."""
        with pytest.raises(AttributeError):
            SAFE_TOOLS.add("new_tool")  # type: ignore[attr-defined]

    def test_destructive_tools_not_in_safe(self):
        """write_to_file is NOT in SAFE_TOOLS."""
        assert "write_to_file" not in SAFE_TOOLS

    def test_run_command_not_in_safe(self):
        """run_command is NOT in SAFE_TOOLS."""
        assert "run_command" not in SAFE_TOOLS


# ---------------------------------------------------------------------------
# DESTRUCTIVE_TOOLS constant
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestDestructiveToolsConstant:
    """DESTRUCTIVE_TOOLS is a frozenset of write/execute tool names."""

    def test_destructive_tools_is_frozenset(self):
        """DESTRUCTIVE_TOOLS is a frozenset instance."""
        assert isinstance(DESTRUCTIVE_TOOLS, frozenset)

    def test_destructive_tools_count(self):
        """DESTRUCTIVE_TOOLS contains exactly 7 tools."""
        assert len(DESTRUCTIVE_TOOLS) == 7

    def test_write_to_file_in_destructive(self):
        """write_to_file is classified as destructive."""
        assert "write_to_file" in DESTRUCTIVE_TOOLS

    def test_run_command_in_destructive(self):
        """run_command is classified as destructive."""
        assert "run_command" in DESTRUCTIVE_TOOLS

    def test_replace_file_content_in_destructive(self):
        """replace_file_content is classified as destructive."""
        assert "replace_file_content" in DESTRUCTIVE_TOOLS

    def test_browser_subagent_in_destructive(self):
        """browser_subagent is classified as destructive."""
        assert "browser_subagent" in DESTRUCTIVE_TOOLS

    def test_generate_image_in_destructive(self):
        """generate_image is classified as destructive."""
        assert "generate_image" in DESTRUCTIVE_TOOLS

    def test_safe_tools_not_in_destructive(self):
        """view_file is NOT in DESTRUCTIVE_TOOLS."""
        assert "view_file" not in DESTRUCTIVE_TOOLS

    def test_safe_and_destructive_disjoint(self):
        """SAFE_TOOLS and DESTRUCTIVE_TOOLS share no elements."""
        assert SAFE_TOOLS.isdisjoint(DESTRUCTIVE_TOOLS)


# ---------------------------------------------------------------------------
# CONTROL_TOOLS constant
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestControlToolsConstant:
    """CONTROL_TOOLS is a frozenset of meta-control tool names."""

    def test_control_tools_is_frozenset(self):
        """CONTROL_TOOLS is a frozenset instance."""
        assert isinstance(CONTROL_TOOLS, frozenset)

    def test_task_boundary_in_control(self):
        """task_boundary is classified as control."""
        assert "task_boundary" in CONTROL_TOOLS

    def test_notify_user_in_control(self):
        """notify_user is classified as control."""
        assert "notify_user" in CONTROL_TOOLS

    def test_control_count(self):
        """CONTROL_TOOLS contains exactly 2 tools."""
        assert len(CONTROL_TOOLS) == 2

    def test_all_three_sets_disjoint(self):
        """SAFE, DESTRUCTIVE, and CONTROL sets share no elements."""
        assert SAFE_TOOLS.isdisjoint(CONTROL_TOOLS)
        assert DESTRUCTIVE_TOOLS.isdisjoint(CONTROL_TOOLS)


# ---------------------------------------------------------------------------
# classify_tool static method
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestClassifyTool:
    """AntigravityToolProvider.classify_tool() static method."""

    def test_classify_view_file_is_safe(self):
        """classify_tool('view_file') returns 'safe'."""
        assert AntigravityToolProvider.classify_tool("view_file") == "safe"

    def test_classify_grep_search_is_safe(self):
        """classify_tool('grep_search') returns 'safe'."""
        assert AntigravityToolProvider.classify_tool("grep_search") == "safe"

    def test_classify_list_dir_is_safe(self):
        """classify_tool('list_dir') returns 'safe'."""
        assert AntigravityToolProvider.classify_tool("list_dir") == "safe"

    def test_classify_write_to_file_is_destructive(self):
        """classify_tool('write_to_file') returns 'destructive'."""
        assert AntigravityToolProvider.classify_tool("write_to_file") == "destructive"

    def test_classify_run_command_is_destructive(self):
        """classify_tool('run_command') returns 'destructive'."""
        assert AntigravityToolProvider.classify_tool("run_command") == "destructive"

    def test_classify_replace_file_content_is_destructive(self):
        """classify_tool('replace_file_content') returns 'destructive'."""
        assert (
            AntigravityToolProvider.classify_tool("replace_file_content")
            == "destructive"
        )

    def test_classify_task_boundary_is_control(self):
        """classify_tool('task_boundary') returns 'control'."""
        assert AntigravityToolProvider.classify_tool("task_boundary") == "control"

    def test_classify_notify_user_is_control(self):
        """classify_tool('notify_user') returns 'control'."""
        assert AntigravityToolProvider.classify_tool("notify_user") == "control"

    def test_classify_unknown_returns_unknown(self):
        """classify_tool with unrecognised name returns 'unknown'."""
        assert AntigravityToolProvider.classify_tool("totally_unknown_xyz") == "unknown"

    def test_classify_empty_string_returns_unknown(self):
        """classify_tool with empty string returns 'unknown'."""
        assert AntigravityToolProvider.classify_tool("") == "unknown"

    def test_classify_all_safe_tools(self):
        """Every name in SAFE_TOOLS classifies as 'safe'."""
        for name in SAFE_TOOLS:
            assert AntigravityToolProvider.classify_tool(name) == "safe", name

    def test_classify_all_destructive_tools(self):
        """Every name in DESTRUCTIVE_TOOLS classifies as 'destructive'."""
        for name in DESTRUCTIVE_TOOLS:
            assert AntigravityToolProvider.classify_tool(name) == "destructive", name

    def test_classify_all_control_tools(self):
        """Every name in CONTROL_TOOLS classifies as 'control'."""
        for name in CONTROL_TOOLS:
            assert AntigravityToolProvider.classify_tool(name) == "control", name


# ---------------------------------------------------------------------------
# get_tool_schema static method
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestGetToolSchema:
    """AntigravityToolProvider.get_tool_schema() static method."""

    def test_schema_for_view_file_not_none(self):
        """get_tool_schema('view_file') returns a dict."""
        schema = AntigravityToolProvider.get_tool_schema("view_file")
        assert schema is not None
        assert isinstance(schema, dict)

    def test_schema_has_description(self):
        """Schema dict for view_file has 'description' key."""
        schema = AntigravityToolProvider.get_tool_schema("view_file")
        assert "description" in schema

    def test_schema_has_parameters(self):
        """Schema dict for view_file has 'parameters' key."""
        schema = AntigravityToolProvider.get_tool_schema("view_file")
        assert "parameters" in schema

    def test_schema_description_is_string(self):
        """Schema description is a non-empty string."""
        schema = AntigravityToolProvider.get_tool_schema("view_file")
        assert isinstance(schema["description"], str)
        assert len(schema["description"]) > 0

    def test_schema_parameters_is_dict(self):
        """Schema parameters is a dict."""
        schema = AntigravityToolProvider.get_tool_schema("view_file")
        assert isinstance(schema["parameters"], dict)

    def test_schema_unknown_returns_none(self):
        """get_tool_schema returns None for unknown tool name."""
        assert AntigravityToolProvider.get_tool_schema("nonexistent_xyz_abc") is None

    def test_schema_for_run_command(self):
        """get_tool_schema works for run_command (destructive tool)."""
        schema = AntigravityToolProvider.get_tool_schema("run_command")
        assert schema is not None
        assert "description" in schema

    def test_schema_for_task_boundary(self):
        """get_tool_schema works for task_boundary (control tool)."""
        schema = AntigravityToolProvider.get_tool_schema("task_boundary")
        assert schema is not None
        assert "parameters" in schema

    def test_all_18_tools_have_valid_schema(self):
        """Every tool returned by list_all_tools() has a valid schema."""
        for name in AntigravityToolProvider.list_all_tools():
            schema = AntigravityToolProvider.get_tool_schema(name)
            assert schema is not None, f"Missing schema for {name!r}"
            assert "description" in schema, f"No description for {name!r}"
            assert "parameters" in schema, f"No parameters for {name!r}"


# ---------------------------------------------------------------------------
# list_all_tools static method
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestListAllTools:
    """AntigravityToolProvider.list_all_tools() static method."""

    def test_list_all_tools_returns_list(self):
        """list_all_tools() returns a list."""
        result = AntigravityToolProvider.list_all_tools()
        assert isinstance(result, list)

    def test_list_all_tools_count_is_18(self):
        """list_all_tools() returns exactly 18 tool names."""
        assert len(AntigravityToolProvider.list_all_tools()) == 18

    def test_list_all_tools_all_strings(self):
        """Every entry in list_all_tools() is a str."""
        for name in AntigravityToolProvider.list_all_tools():
            assert isinstance(name, str)

    def test_list_all_tools_no_duplicates(self):
        """list_all_tools() has no duplicate entries."""
        tools = AntigravityToolProvider.list_all_tools()
        assert len(tools) == len(set(tools))

    def test_list_all_tools_is_sorted(self):
        """list_all_tools() is lexicographically sorted."""
        tools = AntigravityToolProvider.list_all_tools()
        assert tools == sorted(tools)

    def test_list_all_tools_contains_view_file(self):
        """list_all_tools() contains 'view_file'."""
        assert "view_file" in AntigravityToolProvider.list_all_tools()

    def test_list_all_tools_contains_run_command(self):
        """list_all_tools() contains 'run_command'."""
        assert "run_command" in AntigravityToolProvider.list_all_tools()

    def test_list_all_tools_covers_all_categories(self):
        """list_all_tools() includes tools from safe, destructive, and control."""
        tools = set(AntigravityToolProvider.list_all_tools())
        assert SAFE_TOOLS.issubset(tools)
        assert DESTRUCTIVE_TOOLS.issubset(tools)
        assert CONTROL_TOOLS.issubset(tools)


# ---------------------------------------------------------------------------
# AntigravityToolProvider instantiation
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestAntigravityToolProviderInit:
    """AntigravityToolProvider constructor and attributes."""

    def test_provider_instantiates_with_client_object(self):
        """AntigravityToolProvider accepts any object as client."""

        class _FakeClient:
            pass

        provider = AntigravityToolProvider(_FakeClient())
        assert provider is not None

    def test_default_prefix(self):
        """Default prefix is 'antigravity.'."""

        class _FakeClient:
            pass

        provider = AntigravityToolProvider(_FakeClient())
        assert provider.prefix == "antigravity."

    def test_custom_prefix_stored(self):
        """Custom prefix is stored on the instance."""

        class _FakeClient:
            pass

        provider = AntigravityToolProvider(_FakeClient(), prefix="test.")
        assert provider.prefix == "test."

    def test_client_stored_on_instance(self):
        """Client object is stored as provider.client."""

        class _FakeClient:
            id = "fc1"

        fc = _FakeClient()
        provider = AntigravityToolProvider(fc)
        assert provider.client is fc


# ---------------------------------------------------------------------------
# _make_tool_func internal method
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestMakeToolFunc:
    """AntigravityToolProvider._make_tool_func() behaviour."""

    def _make_provider(self):
        """Return a provider with a minimal real client stub."""
        from codomyrmex.ide.antigravity.client import AntigravityClient

        client = AntigravityClient()
        return AntigravityToolProvider(client)

    def test_make_tool_func_returns_callable(self):
        """_make_tool_func returns a callable."""
        provider = self._make_provider()
        func = provider._make_tool_func("view_file")
        assert callable(func)

    def test_make_tool_func_name_matches_tool(self):
        """Returned callable.__name__ matches the tool name."""
        provider = self._make_provider()
        func = provider._make_tool_func("grep_search")
        assert func.__name__ == "grep_search"

    def test_make_tool_func_docstring_from_schema(self):
        """Returned callable has a non-empty docstring from schema."""
        provider = self._make_provider()
        func = provider._make_tool_func("list_dir")
        assert func.__doc__ is not None
        assert len(func.__doc__) > 0

    def test_make_tool_func_unknown_tool_still_callable(self):
        """_make_tool_func for unknown tool still returns a callable."""
        provider = self._make_provider()
        func = provider._make_tool_func("ghost_tool_xyz")
        assert callable(func)
        assert func.__name__ == "ghost_tool_xyz"
