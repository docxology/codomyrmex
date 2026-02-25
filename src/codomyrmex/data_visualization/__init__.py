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

from pathlib import Path
from typing import Any

from . import exceptions, export

# Charts & Plotting Functions
from .charts.area_chart import AreaChart, create_area_chart
from .charts.bar_chart import BarChart
from .charts.box_plot import BoxPlot, create_box_plot
from .charts.heatmap import Heatmap, create_heatmap
from .charts.histogram import Histogram, create_histogram
from .charts.line_plot import LinePlot, create_line_plot
from .charts.pie_chart import PieChart, create_pie_chart
from .charts.scatter_plot import ScatterPlot, create_scatter_plot
from .core.export import render_html
from .core.layout import Grid, Section

# Core
from .core.theme import DARK_THEME, DEFAULT_THEME, Theme
from .core.ui import Card, Dashboard, Table
from .plots.mermaid import MermaidDiagram
from .reports._base import BaseReport as Report
from .reports.finance import FinanceReport

# Reports
from .reports.general import GeneralSystemReport
from .reports.logistics import LogisticsReport
from .reports.marketing import MarketingReport


def create_bar_chart(data: Any, title: str = "Bar Chart") -> Any:
    """Create a bar chart from a dictionary of data."""
    categories = data.get("categories", []) if isinstance(data, dict) else []
    values = data.get("values", []) if isinstance(data, dict) else []
    chart = BarChart(categories=categories, values=values, title=title)
    return chart.render()


# Convenience alias
BarPlot = BarChart


def generate_report(output_dir: str | Path = ".", report_type: str = "general", **kwargs) -> str:
    """Generate an HTML report and save it to disk.

    Args:
        output_dir: Directory to save the report file.
        report_type: One of ``'general'``, ``'finance'``, ``'marketing'``, ``'logistics'``.
        **kwargs: Additional report parameters.

    Returns:
        Absolute path to the generated HTML file.
    """
    report_map = {
        "general": GeneralSystemReport,
        "finance": FinanceReport,
        "marketing": MarketingReport,
        "logistics": LogisticsReport,
    }

    report_cls = report_map.get(report_type, GeneralSystemReport)
    report = report_cls()
    report.generate()

    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    filename = f"{report_type}_report.html"
    out_path = out_dir / filename

    report.dashboard.render(output_path=str(out_path))
    return str(out_path.resolve())


__all__ = [
    "exceptions",
    "export",
    # Core
    "Theme",
    "DEFAULT_THEME",
    "DARK_THEME",
    "Grid",
    "Section",
    "render_html",
    # UI
    "Dashboard",
    "Card",
    "Table",
    # Reports
    "Report",
    "GeneralSystemReport",
    "FinanceReport",
    "MarketingReport",
    "LogisticsReport",
    "generate_report",
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
    # Mermaid
    "MermaidDiagram",
]
