"""
Data Visualization Module for Codomyrmex.

This module provides utilities for generating various types of plots,
visualizations, and interactive dashboards.
"""

# Submodule exports - import first to make available
from . import themes
from . import mermaid
from . import charts

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
except ImportError:
    HAS_ADVANCED_PLOTTER = False
    AdvancedPlotter = None
    ChartStyle = None
    ColorPalette = None
    PlotType = None
    PlotConfig = None
    DataPoint = None
    Dataset = None

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
