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
from .charts.bar_chart import BarChart, create_bar_chart
from .charts.box_plot import BoxPlot, create_box_plot
from .charts.heatmap import Heatmap, create_heatmap
from .charts.histogram import Histogram, create_histogram
from .charts.line_plot import LinePlot, create_line_plot
from .charts.pie_chart import PieChart, create_pie_chart
from .charts.scatter_plot import ScatterPlot, create_scatter_plot

# Convenience functions
from pathlib import Path
from typing import Any


class Dashboard:
    """Dashboard container for visualization components."""

    def __init__(self, title: str = "Dashboard", theme: Theme | None = None):
        self.title = title
        self.theme = theme or DEFAULT_THEME
        self.sections: list[Any] = []

    def add_section(self, section: Any) -> None:
        self.sections.append(section)

    def render(self) -> str:
        inner = "\n".join(
            getattr(s, "render", lambda: str(s))() for s in self.sections
        )
        return f"<div class='dashboard'><h1>{self.title}</h1>{inner}</div>"

    def to_dict(self) -> dict[str, Any]:
        return {
            "title": self.title,
            "theme": self.theme.name,
            "section_count": len(self.sections),
        }


class Card:
    """Card component for dashboards."""

    def __init__(self, title: str = "", content: str = "", **kwargs: Any):
        self.title = title
        self.content = content
        self.kwargs = kwargs

    def render(self) -> str:
        return f"<div class='card'><h3>{self.title}</h3><p>{self.content}</p></div>"


class Table:
    """Table component for data display."""

    def __init__(self, headers: list[str] | None = None, rows: list[list] | None = None, **kwargs):
        self.headers = headers or []
        self.rows = rows or []

    def render(self) -> str:
        header = "".join(f"<th>{h}</th>" for h in self.headers)
        body = "".join(
            "<tr>" + "".join(f"<td>{c}</td>" for c in row) + "</tr>"
            for row in self.rows
        )
        return f"<table><thead><tr>{header}</tr></thead><tbody>{body}</tbody></table>"


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
    "BoxPlot",
    "Heatmap",
    "Histogram",
    "LinePlot",
    "PieChart",
    "ScatterPlot",
]
