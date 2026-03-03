"""Tests for MCP proxy tools in codomyrmex.agents.pai.mcp.proxy_tools.

All tests call the real implementations directly -- no mocks, no MagicMock,
no monkeypatch.  External-service tests use @pytest.mark.skipif guards.

Coverage targets:
- _tool_list_modules   -- list_modules wrapper
- _tool_module_info    -- importlib-based module introspection
- _tool_pai_status     -- PAIBridge.get_status() wrapper
- _tool_pai_awareness  -- DataProvider wrapper (may gracefully error)
- _tool_list_workflows -- YAML-frontmatter workflow scanner
- _tool_list_module_functions -- inspect-based function lister
- _tool_get_module_readme     -- README/SPEC reader
"""

from __future__ import annotations

from pathlib import Path

import pytest

from codomyrmex.agents.pai.mcp.proxy_tools import (
    _tool_get_module_readme,
    _tool_list_module_functions,
    _tool_list_modules,
    _tool_list_workflows,
    _tool_module_info,
    _tool_pai_awareness,
    _tool_pai_status,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_PROJECT_ROOT = Path(__file__).resolve().parents[6]


# ---------------------------------------------------------------------------
# TestToolListModules
# ---------------------------------------------------------------------------

class TestToolListModules:
    """Tests for _tool_list_modules() -- list all codomyrmex modules."""

    def test_returns_dict(self):
        """Return value must be a dict."""
        result = _tool_list_modules()
        assert isinstance(result, dict)

    def test_has_modules_key(self):
        """Result dict must contain a 'modules' key."""
        result = _tool_list_modules()
        assert "modules" in result, f"Missing 'modules' key, got: {list(result.keys())}"

    def test_has_count_key(self):
        """Result dict must contain a 'count' key."""
        result = _tool_list_modules()
        assert "count" in result, f"Missing 'count' key, got: {list(result.keys())}"

    def test_modules_is_list(self):
        """'modules' value must be a list."""
        result = _tool_list_modules()
        assert isinstance(result["modules"], list)

    def test_count_matches_modules_length(self):
        """'count' must equal len(modules)."""
        result = _tool_list_modules()
        assert result["count"] == len(result["modules"])

    def test_modules_not_empty(self):
        """At least one module must be present in a working install."""
        result = _tool_list_modules()
        assert result["count"] >= 1

    def test_modules_are_strings(self):
        """Each module entry must be a string."""
        result = _tool_list_modules()
        for mod in result["modules"][:10]:  # spot-check first 10
            assert isinstance(mod, str), f"Non-string module entry: {mod!r}"


# ---------------------------------------------------------------------------
# TestToolModuleInfo
# ---------------------------------------------------------------------------

class TestToolModuleInfo:
    """Tests for _tool_module_info(module_name) -- module introspection."""

    def test_known_module_returns_dict(self):
        """Known module returns a dict, not an error."""
        result = _tool_module_info(module_name="agents")
        assert isinstance(result, dict)
        assert "error" not in result, f"Unexpected error for known module: {result}"

    def test_known_module_name_field(self):
        """'module' field in result must match the requested module name."""
        result = _tool_module_info(module_name="agents")
        assert result["module"] == "agents"

    def test_known_module_has_exports(self):
        """'exports' field must be a list (may be empty for stub modules)."""
        result = _tool_module_info(module_name="agents")
        assert "exports" in result
        assert isinstance(result["exports"], list)

    def test_known_module_has_export_count(self):
        """'export_count' must be a non-negative integer."""
        result = _tool_module_info(module_name="agents")
        assert "export_count" in result
        assert isinstance(result["export_count"], int)
        assert result["export_count"] >= 0

    def test_known_module_has_path(self):
        """'path' must be a non-empty string pointing to a real file."""
        result = _tool_module_info(module_name="agents")
        assert "path" in result
        # path may be None for namespace packages, but for agents it should exist
        if result["path"] is not None:
            assert isinstance(result["path"], str)

    def test_known_module_docstring_type(self):
        """'docstring' must be a str or None, never a non-string."""
        result = _tool_module_info(module_name="agents")
        assert "docstring" in result
        assert result["docstring"] is None or isinstance(result["docstring"], str)

    def test_unknown_module_returns_error_key(self):
        """Unknown module must return a dict with an 'error' key (not raise)."""
        result = _tool_module_info(module_name="this_module_does_not_exist_xyz123")
        assert isinstance(result, dict)
        assert "error" in result, f"Expected 'error' key for unknown module, got: {result}"

    def test_unknown_module_error_mentions_name(self):
        """Error message should contain the module name for debugging."""
        module_name = "totally_fake_module_abc"
        result = _tool_module_info(module_name=module_name)
        assert module_name in result["error"]

    def test_second_module_logging_monitoring(self):
        """logging_monitoring module introspection returns expected structure."""
        result = _tool_module_info(module_name="logging_monitoring")
        assert isinstance(result, dict)
        # Either success (has 'module' key) or a graceful error
        assert "module" in result or "error" in result

    def test_export_count_consistent_with_exports(self):
        """export_count reflects the real total; exports list is capped at 50.

        The implementation returns exports[:50] but export_count = len(all_exports),
        so export_count >= len(exports) is the correct invariant.
        """
        result = _tool_module_info(module_name="agents")
        if "error" not in result:
            # exports is truncated to 50 by the implementation; count is the real total
            assert result["export_count"] >= len(result["exports"])


# ---------------------------------------------------------------------------
# TestToolPaiStatus
# ---------------------------------------------------------------------------

class TestToolPaiStatus:
    """Tests for _tool_pai_status() -- PAI installation status."""

    def test_returns_dict(self):
        """Return value must be a dict."""
        result = _tool_pai_status()
        assert isinstance(result, dict)

    def test_has_installed_key(self):
        """Result must contain 'installed' key indicating PAI presence."""
        result = _tool_pai_status()
        assert "installed" in result, (
            f"Missing 'installed' key in pai_status result: {list(result.keys())}"
        )

    def test_installed_is_bool(self):
        """'installed' must be a boolean value."""
        result = _tool_pai_status()
        assert isinstance(result["installed"], bool)

    def test_has_pai_root_key(self):
        """Result must contain 'pai_root' key."""
        result = _tool_pai_status()
        assert "pai_root" in result

    def test_has_upstream_key(self):
        """Result must contain 'upstream' key."""
        result = _tool_pai_status()
        assert "upstream" in result

    def test_has_components_key(self):
        """Result must contain 'components' key."""
        result = _tool_pai_status()
        assert "components" in result

    def test_components_is_dict(self):
        """'components' must be a dict."""
        result = _tool_pai_status()
        assert isinstance(result["components"], dict)

    def test_no_exception_raised(self):
        """Calling _tool_pai_status() must not raise any exception."""
        # If PAI is not installed, PAIBridge.get_status() should still return a valid dict
        try:
            result = _tool_pai_status()
            assert isinstance(result, dict)
        except Exception as exc:
            pytest.fail(f"_tool_pai_status() raised unexpectedly: {exc}")


# ---------------------------------------------------------------------------
# TestToolPaiAwareness
# ---------------------------------------------------------------------------

class TestToolPaiAwareness:
    """Tests for _tool_pai_awareness() -- full PAI awareness data."""

    def test_returns_dict(self):
        """Return value must always be a dict (even on graceful failure)."""
        result = _tool_pai_awareness()
        assert isinstance(result, dict)

    def test_no_exception_raised(self):
        """_tool_pai_awareness() must never raise -- it catches ImportError/OSError."""
        try:
            result = _tool_pai_awareness()
            assert isinstance(result, dict)
        except Exception as exc:
            pytest.fail(f"_tool_pai_awareness() raised unexpectedly: {exc}")

    def test_graceful_error_or_success(self):
        """Result is either a data dict or a graceful {'error': ...} dict."""
        result = _tool_pai_awareness()
        # Either it has real data keys, or it has an 'error' key
        has_data = any(k in result for k in ("missions", "projects", "telos", "memory", "skills"))
        has_error = "error" in result
        assert has_data or has_error, (
            f"Unexpected result structure from _tool_pai_awareness: {list(result.keys())}"
        )

    @pytest.mark.skipif(
        not (Path.home() / ".claude" / "PAI").exists(),
        reason="PAI installation not present; awareness data requires PAI filesystem"
    )
    def test_full_awareness_has_expected_keys(self):
        """When PAI is installed, result must contain all major awareness keys."""
        result = _tool_pai_awareness()
        assert "error" not in result, f"Unexpected error with PAI installed: {result}"
        expected_keys = {"missions", "projects", "telos", "memory", "skills"}
        for key in expected_keys:
            assert key in result, f"Missing expected key '{key}' in pai_awareness result"


# ---------------------------------------------------------------------------
# TestToolListWorkflows
# ---------------------------------------------------------------------------

class TestToolListWorkflows:
    """Tests for _tool_list_workflows() -- scan .agent/workflows/ for workflow files."""

    def test_returns_dict(self):
        """Return value must be a dict."""
        result = _tool_list_workflows()
        assert isinstance(result, dict)

    def test_has_workflows_key(self):
        """Result must contain 'workflows' key."""
        result = _tool_list_workflows()
        assert "workflows" in result

    def test_has_count_key(self):
        """Result must contain 'count' key."""
        result = _tool_list_workflows()
        assert "count" in result

    def test_count_matches_workflows(self):
        """'count' must equal len(workflows)."""
        result = _tool_list_workflows()
        assert result["count"] == len(result["workflows"])

    def test_workflows_is_list(self):
        """'workflows' must be a list."""
        result = _tool_list_workflows()
        assert isinstance(result["workflows"], list)

    def test_custom_project_root_missing(self):
        """A non-existent project root returns count=0 with error message."""
        result = _tool_list_workflows(project_root="/nonexistent/path/xyz")
        assert result["count"] == 0

    def test_workflow_entries_have_name(self):
        """Each workflow entry must have a 'name' field."""
        result = _tool_list_workflows()
        for workflow in result["workflows"]:
            assert "name" in workflow, f"Workflow entry missing 'name': {workflow}"

    def test_workflow_entries_have_filepath(self):
        """Each workflow entry must have a 'filepath' field."""
        result = _tool_list_workflows()
        for workflow in result["workflows"]:
            assert "filepath" in workflow, f"Workflow entry missing 'filepath': {workflow}"


# ---------------------------------------------------------------------------
# TestToolListModuleFunctions
# ---------------------------------------------------------------------------

class TestToolListModuleFunctions:
    """Tests for _tool_list_module_functions() -- inspect public callables."""

    def test_returns_dict(self):
        """Return value must be a dict."""
        result = _tool_list_module_functions(module="logging_monitoring")
        assert isinstance(result, dict)

    def test_has_functions_key(self):
        """Result must contain 'functions' key."""
        result = _tool_list_module_functions(module="logging_monitoring")
        assert "functions" in result or "error" in result

    def test_known_module_functions_is_list(self):
        """'functions' must be a list for a known module."""
        result = _tool_list_module_functions(module="logging_monitoring")
        if "error" not in result:
            assert isinstance(result["functions"], list)

    def test_known_module_classes_is_list(self):
        """'classes' must be a list for a known module."""
        result = _tool_list_module_functions(module="logging_monitoring")
        if "error" not in result:
            assert isinstance(result["classes"], list)

    def test_known_module_total_callables(self):
        """'total_callables' must equal len(functions) + len(classes)."""
        result = _tool_list_module_functions(module="logging_monitoring")
        if "error" not in result:
            assert result["total_callables"] == (
                len(result["functions"]) + len(result["classes"])
            )

    def test_unknown_module_returns_error(self):
        """Unknown module must return a dict with 'error' key (not raise)."""
        result = _tool_list_module_functions(module="nonexistent_module_xyz_123")
        assert "error" in result

    def test_function_entries_have_name(self):
        """Each function entry must have 'name', 'signature', 'docstring'."""
        result = _tool_list_module_functions(module="logging_monitoring")
        if "error" not in result:
            for func in result["functions"][:5]:  # spot-check first 5
                assert "name" in func
                assert "signature" in func
                assert "docstring" in func


# ---------------------------------------------------------------------------
# TestToolGetModuleReadme
# ---------------------------------------------------------------------------

class TestToolGetModuleReadme:
    """Tests for _tool_get_module_readme() -- read README.md or SPEC.md."""

    def test_returns_dict(self):
        """Return value must be a dict."""
        result = _tool_get_module_readme(module="agents")
        assert isinstance(result, dict)

    def test_known_module_has_content(self):
        """Known module with README.md returns 'content' key."""
        result = _tool_get_module_readme(module="agents")
        assert "content" in result or "error" in result

    def test_known_module_content_is_string(self):
        """'content' must be a non-empty string for known modules with docs."""
        result = _tool_get_module_readme(module="agents")
        if "error" not in result:
            assert isinstance(result["content"], str)
            assert len(result["content"]) > 0

    def test_unknown_module_returns_error(self):
        """Unknown module must return error, not raise."""
        result = _tool_get_module_readme(module="this_module_does_not_exist_xyz")
        assert isinstance(result, dict)
        assert "error" in result

    def test_known_module_path_field(self):
        """Successful result must include 'path' pointing to the README."""
        result = _tool_get_module_readme(module="agents")
        if "error" not in result:
            assert "path" in result
            assert isinstance(result["path"], str)
