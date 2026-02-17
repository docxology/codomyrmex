"""Line plot visualization module.

Provides create_line_plot function for creating line plot visualizations.
"""

from typing import Any
from pathlib import Path


def create_line_plot(
    data: list[dict[str, Any]] | None = None,
    x: str = "x",
    y: str = "y",
    title: str = "Line Plot",
    output_path: str | Path | None = None,
    **kwargs: Any,
) -> dict[str, Any]:
    """Create a line plot visualization.

    Args:
        data: List of data points.
        x: Name of x-axis field.
        y: Name of y-axis field.
        title: Plot title.
        output_path: Optional output file path.
        **kwargs: Additional plot configuration.

    Returns:
        Dict with plot configuration and data.
    """
    return {
        "type": "line_plot",
        "title": title,
        "x": x,
        "y": y,
        "data": data or [],
        "config": kwargs,
        "output_path": str(output_path) if output_path else None,
    }
