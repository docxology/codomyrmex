"""Strictly zero-mock tests for plugin_system MCP tools."""

from codomyrmex.plugin_system.mcp_tools import plugin_resolve_dependencies, plugin_scan_entry_points

def test_plugin_scan_entry_points_success():
    """Test successful plugin discovery from entry points without mocking."""
    # We use a non-existent group so we get a clean result without actual side effects
    result = plugin_scan_entry_points(entry_point_group="codomyrmex.tests.empty_plugins")

    assert result["status"] == "ok"
    assert "plugin_count" in result
    assert result["plugin_count"] == 0
    assert "plugins" in result
    assert result["plugins"] == []
    assert "errors" in result

def test_plugin_scan_entry_points_error():
    """Test error handling in plugin discovery by passing invalid arguments to native calls."""
    class BadGroup:
        # Cause exception during getattr or when used as string
        @property
        def __class__(self):
            raise ValueError("Intentional error for zero mock testing")

        def __str__(self):
            raise ValueError("Intentional error for zero mock testing")

    result = plugin_scan_entry_points(entry_point_group=BadGroup()) # type: ignore
    assert result["status"] == "error"
    assert "error" in result

def test_plugin_resolve_dependencies_success():
    """Test successful plugin dependency resolution without mocking."""
    plugins = [
        {"name": "plugin_a", "dependencies": []},
        {"name": "plugin_b", "dependencies": ["plugin_a"]},
        {"name": "plugin_c", "dependencies": ["plugin_b"]},
    ]

    result = plugin_resolve_dependencies(plugins=plugins)

    assert result["status"] == "ok"
    assert result["resolution_status"] == "resolved"
    assert result["load_order"] == ["plugin_a", "plugin_b", "plugin_c"]
    assert result["missing"] == []
    assert result["circular"] == []

def test_plugin_resolve_dependencies_missing():
    """Test dependency resolution with missing dependencies."""
    plugins = [
        {"name": "plugin_a", "dependencies": ["non_existent_plugin"]},
    ]

    result = plugin_resolve_dependencies(plugins=plugins)

    assert result["status"] == "ok"
    assert result["resolution_status"] == "missing"
    assert result["missing"] == ["non_existent_plugin"]
    assert result["load_order"] == []

def test_plugin_resolve_dependencies_circular():
    """Test dependency resolution with circular dependencies."""
    plugins = [
        {"name": "plugin_a", "dependencies": ["plugin_b"]},
        {"name": "plugin_b", "dependencies": ["plugin_a"]},
    ]

    result = plugin_resolve_dependencies(plugins=plugins)

    assert result["status"] == "ok"
    assert result["resolution_status"] == "circular"
    assert len(result["circular"]) > 0

def test_plugin_resolve_dependencies_error():
    """Test error handling by providing invalid input format."""
    # Pass a list of integers instead of a list of dicts to trigger a native TypeError/KeyError
    plugins = [1, 2, 3]

    result = plugin_resolve_dependencies(plugins=plugins) # type: ignore

    assert result["status"] == "error"
    assert "error" in result
