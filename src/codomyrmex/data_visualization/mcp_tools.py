"""MCP tools for the data_visualization module."""

from typing import Any

from codomyrmex.model_context_protocol.decorators import mcp_tool


@mcp_tool(category="data_visualization")
def generate_chart(
    chart_type: str,
    data: dict[str, Any],
    title: str = "Chart",
    output_path: str | None = None
) -> dict:
    """Generate a visualization chart and optionally save it.
    
    Args:
        chart_type: Type of chart ('bar', 'pie', 'line', 'scatter', 'area', 'histogram')
        data: Dictionary containing chart data (structure depends on type)
        title: Title of the chart
        output_path: Optional path to save the rendered output
        
    Returns:
        A dictionary containing the chart schema or generation status.
    """
    import codomyrmex.data_visualization as dv

    chart_factories = {
        "bar": dv.create_bar_chart,
        "pie": dv.create_pie_chart,
        "line": dv.create_line_plot,
        "scatter": dv.create_scatter_plot,
        "area": dv.create_area_chart,
        "histogram": dv.create_histogram
    }

    if chart_type not in chart_factories:
        return {"status": "error", "message": f"Unsupported chart type: {chart_type}"}

    try:
        factory = chart_factories[chart_type]

        # Some factories might have different signatures, mapping basic ones
        if chart_type == "bar":
            result = factory(data, title=title)
        else:
            # Fallback for dynamic unpacking based on the provided dictionary
            result = factory(**data)

        response: dict = {
            "status": "success",
            "rendered": True,
            "chart_type": chart_type,
            "chart": result,
        }

        if output_path and result is not None:
            import os
            os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(str(result))
            response["output_path"] = output_path

        return response
    except Exception as e:
        return {"status": "error", "message": str(e)}


@mcp_tool(category="data_visualization")
def export_dashboard(report_type: str = "general", output_dir: str = ".") -> dict:
    """Generate and export a comprehensive HTML dashboard report.
    
    Args:
        report_type: Type of report ('general', 'finance', 'marketing', 'logistics')
        output_dir: Directory where the HTML report will be saved
        
    Returns:
        A dictionary containing the export status and file path.
    """
    from codomyrmex.data_visualization import generate_report

    try:
        file_path = generate_report(output_dir=output_dir, report_type=report_type)
        return {
            "status": "success",
            "message": "Dashboard exported successfully",
            "file_path": file_path
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}
