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
from .plots.violin import ViolinPlot
from .plots.radar import RadarChart
from .plots.candlestick import CandlestickChart
from .plots.gantt import GanttChart
from .plots.funnel import FunnelChart
from .plots.sankey import SankeyDiagram
from .plots.wordcloud import WordCloud
from .plots.confusion_matrix import ConfusionMatrix
from .plots.treemap import TreeMap
from .plots.network import NetworkGraph

# Components
from .components.basic import Card, Table
from .components.media import Image, Video
from .components.text import TextBlock, CodeBlock
from .components.badge import Badge
from .components.alert import Alert
from .components.progress import ProgressBar
from .components.timeline import Timeline, TimelineEvent
from .components.statbox import StatBox
from .components.chat_bubble import ChatBubble
from .components.json_view import JsonView
from .components.heatmap_table import HeatmapTable

# Reports
from .reports.base import Report
from .reports.general import GeneralSystemReport

from .reports.finance import FinanceReport
from .reports.marketing import MarketingReport
from .reports.logistics import LogisticsReport

# Backward compatibility function (renamed/wrapped)
from codomyrmex.model_context_protocol.decorators import mcp_tool

@mcp_tool(category="visualization")
def generate_report(output_dir: str = "report_output", report_type: str = "general") -> str:
    from pathlib import Path
    out_path = Path(output_dir) / f"{report_type}_report.html"
    
    if report_type == "finance":
        report = FinanceReport()
    elif report_type == "marketing":
        report = MarketingReport()
    elif report_type == "logistics":
        report = LogisticsReport()
    else:
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
    "ViolinPlot",
    "RadarChart",
    "CandlestickChart",
    "GanttChart",
    "FunnelChart",
    "SankeyDiagram",
    "WordCloud",
    "ConfusionMatrix",
    "TreeMap",
    "NetworkGraph",
    "Card",
    "Table",
    "Image",
    "Video",
    "TextBlock",
    "CodeBlock",
    "Badge",
    "Alert",
    "ProgressBar",
    "Timeline",
    "TimelineEvent",
    "StatBox",
    "ChatBubble",
    "JsonView",
    "HeatmapTable",
    "Report",
    "GeneralSystemReport",
    "FinanceReport",
    "MarketingReport",
    "LogisticsReport",
    "generate_report"
]
