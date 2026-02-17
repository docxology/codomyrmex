"""Bar chart visualization module.

Provides create_bar_chart function for creating bar chart visualizations.
"""

from typing import Any
from pathlib import Path


def create_bar_chart(
    data: list[dict[str, Any]] | None = None,
    x: str = "category",
    y: str = "value",
    title: str = "Bar Chart",
    output_path: str | Path | None = None,
    **kwargs: Any,
) -> dict[str, Any]:
    """Create a bar chart visualization.

    Args:
        data: List of data points.
        x: Name of category field.
        y: Name of value field.
        title: Chart title.
        output_path: Optional output file path.
        **kwargs: Additional chart configuration.

    Returns:
        Dict with chart configuration and data.
    """
    return {
        "type": "bar_chart",
        "title": title,
        "x": x,
        "y": y,
        "data": data or [],
        "config": kwargs,
        "output_path": str(output_path) if output_path else None,
    }
