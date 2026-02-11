"""
Central Visualization Module for Codomyrmex.

Provides a unified interface for accessing visualizations across all modules
and generating comprehensive dashboards.
"""

# Core
from .core.dashboard import Dashboard
from .core.layout import Grid
from .core.theme import Theme

# Plots
from .plots.base import Plot
from .plots.scatter import ScatterPlot
from .plots.heatmap import Heatmap
from .plots.mermaid import MermaidDiagram
from .plots.bar import BarPlot
from .plots.line import LinePlot
from .plots.histogram import Histogram
from .plots.pie import PieChart
from .plots.box import BoxPlot
from .plots.area import AreaPlot

# Components
from .components.basic import Card, Table
from .components.media import Image, Video
from .components.text import TextBlock, CodeBlock

# Reports
from .reports.base import Report
from .reports.general import GeneralSystemReport

# Backward compatibility function (renamed/wrapped)
def generate_report(output_dir: str = "report_output") -> str:
    from pathlib import Path
    out_path = Path(output_dir) / "index.html"
    report = GeneralSystemReport()
    return report.save(str(out_path))

__all__ = [
    "Dashboard", 
    "Grid", 
    "Theme", 
    "Plot", 
    "ScatterPlot", 
    "Heatmap", 
    "MermaidDiagram",
    "BarPlot",
    "LinePlot",
    "Histogram",
    "PieChart",
    "BoxPlot",
    "AreaPlot",
    "Card",
    "Table",
    "Image",
    "Video",
    "TextBlock",
    "CodeBlock",
    "Report",
    "GeneralSystemReport",
    "generate_report"
]
