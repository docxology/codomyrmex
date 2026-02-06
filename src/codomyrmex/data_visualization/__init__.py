"""
Data Visualization Module for Codomyrmex.

This module provides utilities for generating various types of plots,
visualizations, and interactive dashboards.
"""

# Submodule exports - import first to make available
from . import charts, mermaid, themes

# Try optional submodules
try:
    from . import engines
except ImportError:
    pass

try:
    from . import git
except ImportError:
    pass

# Try to import from existing modules, but don't fail if they don't exist
try:
    from .engines.advanced_plotter import (
        AdvancedPlotter,
        ChartStyle,
        ColorPalette,
        DataPoint,
        Dataset,
        PlotConfig,
        PlotType,
        create_advanced_bar_chart,
        create_advanced_dashboard,
        create_advanced_heatmap,
        create_advanced_histogram,
        create_advanced_line_plot,
        create_advanced_scatter_plot,
    )

    # Create simpler aliases for advanced functions
    create_line_plot = create_advanced_line_plot
    create_scatter_plot = create_advanced_scatter_plot
    create_bar_chart = create_advanced_bar_chart
    create_histogram = create_advanced_histogram
    create_heatmap_advanced = create_advanced_heatmap
    create_dashboard = create_advanced_dashboard

    HAS_ADVANCED_PLOTTER = True
    HAS_BASIC_CHARTS = False  # Not needed when advanced plotter is available
except ImportError:
    HAS_ADVANCED_PLOTTER = False
    AdvancedPlotter = None

    # Provide stub enums so scripts can iterate over them
    from enum import Enum

    class ChartStyle(Enum):
        """Fallback chart style enum."""
        DEFAULT = "default"
        MINIMAL = "minimal"
        MODERN = "modern"
        CLASSIC = "classic"
        DARK = "dark"

    class ColorPalette(Enum):
        """Fallback color palette enum."""
        DEFAULT = "default"
        VIRIDIS = "viridis"
        PLASMA = "plasma"
        CIVIDIS = "cividis"
        RAINBOW = "rainbow"

    class PlotType(Enum):
        """Fallback plot type enum."""
        LINE = "line"
        BAR = "bar"
        SCATTER = "scatter"
        HISTOGRAM = "histogram"
        PIE = "pie"

    PlotConfig = None
    DataPoint = None
    Dataset = None

    # Fallback to basic chart functions from charts module
    try:
        from .charts.bar_chart import BarChart, create_bar_chart
        from .charts.histogram import Histogram, create_histogram
        from .charts.line_plot import LinePlot, create_line_plot
        from .charts.pie_chart import PieChart, create_pie_chart
        from .charts.scatter_plot import ScatterPlot, create_scatter_plot
        HAS_BASIC_CHARTS = True
    except ImportError:
        HAS_BASIC_CHARTS = False
        create_bar_chart = None
        create_line_plot = None
        create_scatter_plot = None
        create_histogram = None
        create_pie_chart = None

# Import heatmap from charts (always available)
try:
    from .charts.heatmap import Heatmap, create_heatmap
except ImportError:
    create_heatmap = None
    Heatmap = None

# Import new chart types
try:
    from .charts.box_plot import BoxPlot, create_box_plot
except ImportError:
    create_box_plot = None
    BoxPlot = None

try:
    from .charts.area_chart import AreaChart, create_area_chart
except ImportError:
    create_area_chart = None
    AreaChart = None

try:
    from .git.git_visualizer import (
        GitVisualizer,
        create_git_tree_mermaid,
        create_git_tree_png,
        visualize_git_repository,
    )
    HAS_GIT_VIZ = True
except ImportError:
    HAS_GIT_VIZ = False
    GitVisualizer = None

try:
    from .mermaid.mermaid_generator import (
        MermaidDiagramGenerator,
        create_commit_timeline_diagram,
        create_git_branch_diagram,
        create_git_workflow_diagram,
        create_repository_structure_diagram,
    )
    HAS_MERMAID_GEN = True
except ImportError:
    HAS_MERMAID_GEN = False
    MermaidDiagramGenerator = None

# Backward-compatibility: register charts submodules as direct children of data_visualization
# so that `from codomyrmex.data_visualization.line_plot import ...` still works
import sys as _sys

from .charts import (  # noqa: F401
    bar_chart,
    histogram,
    line_plot,
    pie_chart,
    plot_utils,
    scatter_plot,
)

_pkg = "codomyrmex.data_visualization"
_sys.modules[f"{_pkg}.line_plot"] = line_plot
_sys.modules[f"{_pkg}.bar_chart"] = bar_chart
_sys.modules[f"{_pkg}.scatter_plot"] = scatter_plot
_sys.modules[f"{_pkg}.histogram"] = histogram
_sys.modules[f"{_pkg}.pie_chart"] = pie_chart
_sys.modules[f"{_pkg}.plot_utils"] = plot_utils

try:
    from .charts import heatmap  # noqa: F401
    _sys.modules[f"{_pkg}.heatmap"] = heatmap
except ImportError:
    pass

try:
    from .engines import plotter  # noqa: F401
    _sys.modules[f"{_pkg}.plotter"] = plotter
except ImportError:
    pass

try:
    from .git import git_visualizer  # noqa: F401
    _sys.modules[f"{_pkg}.git_visualizer"] = git_visualizer
except ImportError:
    pass


# Helper functions
def get_available_styles():
    """Get available chart styles."""
    if ChartStyle:
        return [s.value for s in ChartStyle]
    return []

def get_available_palettes():
    """Get available color palettes."""
    if ColorPalette:
        return [p.value for p in ColorPalette]
    return []

def get_available_plot_types():
    """Get available plot types."""
    if PlotType:
        return [t.value for t in PlotType]
    return []

__all__ = [
    "themes",
    "mermaid",
    "charts",
    "get_available_styles",
    "get_available_palettes",
    "get_available_plot_types",
    "create_heatmap",
    "create_box_plot",
    "create_area_chart",
]

if HAS_ADVANCED_PLOTTER:
    __all__.extend([
        "AdvancedPlotter",
        "ChartStyle",
        "ColorPalette",
        "PlotType",
        "PlotConfig",
        "DataPoint",
        "Dataset",
        "create_line_plot",
        "create_scatter_plot",
        "create_bar_chart",
        "create_histogram",
        "create_dashboard",
    ])
elif HAS_BASIC_CHARTS:
    # Export basic chart functions as fallback
    __all__.extend([
        "create_line_plot",
        "create_scatter_plot",
        "create_bar_chart",
        "create_histogram",
        "create_pie_chart",
        "LinePlot",
        "ScatterPlot",
        "BarChart",
        "Histogram",
        "PieChart",
    ])

if HAS_GIT_VIZ:
    __all__.extend([
        "GitVisualizer",
        "create_git_tree_mermaid",
        "create_git_tree_png",
        "visualize_git_repository",
    ])

if HAS_MERMAID_GEN:
    __all__.extend([
        "MermaidDiagramGenerator",
        "create_commit_timeline_diagram",
        "create_git_branch_diagram",
        "create_git_workflow_diagram",
        "create_repository_structure_diagram",
    ])

__version__ = "0.1.0"
