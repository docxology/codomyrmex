"""
Visualization MCP tools.
"""

from codomyrmex.model_context_protocol.tool_decorator import mcp_tool

@mcp_tool(
    name="viz_list_chart_types",
    description="List supported chart types for visualization.",
    category="visualization"
)
def viz_list_chart_types() -> list[str]:
    """List supported chart types."""
    return ["bar", "line", "pie", "scatter"]


@mcp_tool(
    name="viz_create_chart",
    description="Create a chart from data.",
    category="visualization"
)
def viz_create_chart(data: dict, chart_type: str, title: str = "") -> str:
    """
    Create a chart from data.

    Args:
        data: The data for the chart.
        chart_type: The type of chart to create.
        title: The title of the chart.
    """
    if chart_type not in ["bar", "line", "pie", "scatter"]:
        return f"Error: Unsupported chart type '{chart_type}'"

    num_points = len(data)
    title_str = f"'{title}'" if title else "Untitled"
    return f"Chart {title_str} of type '{chart_type}' created with {num_points} data points"


@mcp_tool(
    name="viz_export_chart",
    description="Export a chart to an image file.",
    category="visualization"
)
def viz_export_chart(chart_id: str, format: str = "png", filepath: str = "") -> str:
    """
    Export a chart to an image file.

    Args:
        chart_id: The ID of the chart to export.
        format: The image format (e.g. 'png', 'svg', 'jpeg').
        filepath: The path to save the exported chart to.
    """
    supported_formats = ["png", "svg", "jpeg", "pdf"]
    if format.lower() not in supported_formats:
        return f"Error: Unsupported export format '{format}'"

    path = filepath if filepath else f"{chart_id}.{format}"
    return f"Chart '{chart_id}' exported to {path} in {format.upper()} format"
