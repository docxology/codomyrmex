"""
Data Visualization Module - Unified

Submodules:
    core: Theme, layout, and export utilities
    charts: Chart types (bar, line, scatter, heatmap, etc.)
    plots: Plot components (scatter, histogram, pie, etc.)
    components: UI components (text, media, badges, etc.)
    reports: Report generators (general, finance, marketing, logistics)
    engines: Plotting engine abstraction
    mermaid: Mermaid diagram generation
    themes: Visual themes
    git: Git commit visualization
"""

__version__ = "0.1.0"

from typing import Any, Dict
from . import exceptions
from . import export

# Core
from .core.theme import Theme, DEFAULT_THEME, DARK_THEME
from .core.layout import Grid, Section

# Reports
from .reports.general import GeneralSystemReport
from .reports._base import BaseReport as Report

# Charts & Plotting Functions
from .charts.area_chart import AreaChart, create_area_chart
from .charts.bar_chart import BarChart
from .charts.box_plot import BoxPlot, create_box_plot

def create_bar_chart(data: Any, title: str = "Bar Chart") -> Any:
    """Create a bar chart from a dictionary of data."""
    # Extract categories and values from the data dictionary if possible
    categories = data.get("categories", []) if isinstance(data, dict) else []
    values = data.get("values", []) if isinstance(data, dict) else []
    
    # Initialize BarChart with extracted data
    chart = BarChart(categories=categories, values=values, title=title)
    return chart.render()
from .charts.heatmap import Heatmap, create_heatmap
from .charts.histogram import Histogram, create_histogram
from .charts.line_plot import LinePlot, create_line_plot
from .charts.pie_chart import PieChart, create_pie_chart
from .charts.scatter_plot import ScatterPlot, create_scatter_plot

# Convenience functions
from pathlib import Path
from typing import Any


from .core.ui import Dashboard, Card, Table


class BarPlot:
    """Bar plot visualization."""

    def __init__(self, data: list | None = None, title: str = "", **kwargs):
        self.data = data or []
        self.title = title

    def render(self) -> str:
        return f"<div class='barplot'><h3>{self.title}</h3></div>"


def generate_report(title: str = "Report", output_dir: str | Path | None = None, **kwargs) -> str:
    """Generate an HTML report.

    Args:
        title: Report title.
        output_dir: Optional directory to save the report.
        **kwargs: Additional report parameters.

    Returns:
        HTML string of the generated report.
    """
    from .core.export import render_html

    content = f"<h2>{title}</h2><p>Generated report</p>"
    html = render_html(content, title=title)

    if output_dir:
        output_path = Path(output_dir) / f"{title.lower().replace(' ', '_')}.html"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(html)

    return html

BarPlot = BarChart

__all__ = [
    "exceptions",
    "export",
    # Core
    "Theme",
    "DEFAULT_THEME",
    "DARK_THEME",
    "Grid",
    "Section",
    # Plots
    "Dashboard",
    "Card",
    "Table",
    # Chart Creation Functions
    "create_area_chart",
    "create_bar_chart",
    "create_box_plot",
    "create_heatmap",
    "create_histogram",
    "create_line_plot",
    "create_pie_chart",
    "create_scatter_plot",
    # Chart Classes
    "AreaChart",
    "BarChart",
    "BarPlot",
    "BoxPlot",
    "Heatmap",
    "Histogram",
    "LinePlot",
    "PieChart",
    "ScatterPlot",
]
