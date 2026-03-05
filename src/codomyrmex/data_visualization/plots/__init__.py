"""Plot components for data visualization.

Provides chart types: Heatmap, MermaidDiagram, Histogram,
PieChart, BoxPlot, AreaPlot, ViolinPlot, RadarChart, CandlestickChart,
GanttChart, FunnelChart, SankeyDiagram, WordCloud, ConfusionMatrix,
TreeMap, NetworkGraph, BarChart, LinePlot.

For scatter plots use ``codomyrmex.data_visualization.charts.scatter_plot.ScatterPlot``.
"""

from ._base import BasePlot
from .area import AreaPlot
from .bar_chart import BarChart
from .box import BoxPlot
from .candlestick import CandlestickChart
from .confusion_matrix import ConfusionMatrix
from .funnel import FunnelChart
from .gantt import GanttChart
from .heatmap import Heatmap
from .histogram import Histogram
from .line_plot import LinePlot
from .mermaid import MermaidDiagram
from .network import NetworkGraph
from .pie import PieChart
from .radar import RadarChart
from .sankey import SankeyDiagram
from .treemap import TreeMap
from .violin import ViolinPlot
from .wordcloud import WordCloud

__all__ = [
    "AreaPlot",
    "BarChart",
    "BasePlot",
    "BoxPlot",
    "CandlestickChart",
    "ConfusionMatrix",
    "FunnelChart",
    "GanttChart",
    "Heatmap",
    "Histogram",
    "LinePlot",
    "MermaidDiagram",
    "NetworkGraph",
    "PieChart",
    "RadarChart",
    "SankeyDiagram",
    "TreeMap",
    "ViolinPlot",
    "WordCloud",
]
