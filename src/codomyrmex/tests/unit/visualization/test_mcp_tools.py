"""
Unit tests for visualization MCP tools.
"""

from codomyrmex.visualization.mcp_tools import (
    viz_create_chart,
    viz_export_chart,
    viz_list_chart_types,
)


def test_viz_list_chart_types():
    """Test viz_list_chart_types."""
    types = viz_list_chart_types()
    assert isinstance(types, list)
    assert "bar" in types
    assert "line" in types
    assert "pie" in types
    assert "scatter" in types


def test_viz_create_chart_success():
    """Test viz_create_chart with valid inputs."""
    data = {"A": 10, "B": 20, "C": 30}
    result = viz_create_chart(data, "bar", "Sales Data")

    assert "Chart 'Sales Data' of type 'bar'" in result
    assert "3 data points" in result


def test_viz_create_chart_no_title():
    """Test viz_create_chart without a title."""
    data = {"A": 10, "B": 20}
    result = viz_create_chart(data, "pie")

    assert "Chart Untitled of type 'pie'" in result
    assert "2 data points" in result


def test_viz_create_chart_invalid_type():
    """Test viz_create_chart with an invalid chart type."""
    data = {"A": 10}
    result = viz_create_chart(data, "invalid_type")

    assert "Error: Unsupported chart type" in result


def test_viz_export_chart_success():
    """Test viz_export_chart with valid inputs and default path."""
    result = viz_export_chart("chart123", "png")

    assert "Chart 'chart123' exported to chart123.png" in result
    assert "PNG format" in result


def test_viz_export_chart_custom_path():
    """Test viz_export_chart with a custom filepath."""
    result = viz_export_chart("chart456", "svg", "/tmp/mychart.svg")

    assert "Chart 'chart456' exported to /tmp/mychart.svg" in result
    assert "SVG format" in result


def test_viz_export_chart_invalid_format():
    """Test viz_export_chart with an invalid format."""
    result = viz_export_chart("chart789", "xyz")

    assert "Error: Unsupported export format" in result


def test_mcp_decorator_metadata():
    """Test that the @mcp_tool decorator successfully added metadata."""
    assert hasattr(viz_list_chart_types, "_mcp_tool_meta")
    assert viz_list_chart_types._mcp_tool_meta["name"] == "codomyrmex.viz_list_chart_types"
    assert viz_list_chart_types._mcp_tool_meta["category"] == "visualization"

    assert hasattr(viz_create_chart, "_mcp_tool_meta")
    assert viz_create_chart._mcp_tool_meta["name"] == "codomyrmex.viz_create_chart"
    assert "data" in viz_create_chart._mcp_tool_meta["schema"]["properties"]

    assert hasattr(viz_export_chart, "_mcp_tool_meta")
    assert viz_export_chart._mcp_tool_meta["name"] == "codomyrmex.viz_export_chart"
