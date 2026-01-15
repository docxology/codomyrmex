"""
Data Visualization Module for Codomyrmex.

This module provides utilities for generating various types of plots,
visualizations, and interactive dashboards.

Integration:
- Uses `logging_monitoring` for all logging (ensure `setup_logging()` is called in your main app).
- Relies on `environment_setup` for environment and dependency checks (see project setup docs).

Available functions:
- create_line_plot: Line plot creation
- create_scatter_plot: Scatter plot creation
- create_bar_chart: Bar chart creation
- create_histogram: Histogram creation
- create_pie_chart: Pie chart creation
- create_heatmap: Heatmap creation
- create_line_plot: Line plot with styling options
- create_scatter_plot: Scatter plot with styling options
- create_bar_chart: Bar chart with styling options
- create_histogram: Histogram with styling options
- create_heatmap: Heatmap with styling options
- create_dashboard: Multi-panel dashboard creation
- get_available_styles: Get available chart styles
- get_available_palettes: Get available color palettes
- get_available_plot_types: Get available plot types

Data structures:
- AdvancedPlotter: Main plotting class
- PlotConfig: Configuration for plot generation
- DataPoint: Individual data point for plotting
- Dataset: Dataset for plotting
- PlotType: Types of plots available
- ChartStyle: Chart styling options
- ColorPalette: Color palette options
"""

from .advanced_plotter import (
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

# Helper functions - these are methods on AdvancedPlotter
def get_available_styles():
    """Get available chart styles."""
    return [s.value for s in ChartStyle]

def get_available_palettes():
    """Get available color palettes."""
    return [p.value for p in ColorPalette]

def get_available_plot_types():
    """Get available plot types."""
    return [t.value for t in PlotType]
from .git_visualizer import (
    GitVisualizer,
    create_git_tree_mermaid,
    create_git_tree_png,
    visualize_git_repository,
)
from .mermaid_generator import (
    MermaidDiagramGenerator,
    create_commit_timeline_diagram,
    create_git_branch_diagram,
    create_git_workflow_diagram,
    create_repository_structure_diagram,
)
from .plotter import (
    create_pie_chart,
)

__all__ = [
    # Core plotting functions
    "create_line_plot",
    "create_scatter_plot",
    "create_bar_chart",
    "create_histogram",
    "create_pie_chart",
    "create_heatmap",
    # Plotting functions
    "AdvancedPlotter",
    "create_line_plot",
    "create_scatter_plot",
    "create_bar_chart",
    "create_histogram",
    "create_heatmap",
    "create_dashboard",
    "get_available_styles",
    "get_available_palettes",
    "get_available_plot_types",
    # Data structures
    "PlotConfig",
    "DataPoint",
    "Dataset",
    "PlotType",
    "ChartStyle",
    "ColorPalette",
    # Mermaid diagram functions
    "MermaidDiagramGenerator",
    "create_git_branch_diagram",
    "create_git_workflow_diagram",
    "create_repository_structure_diagram",
    "create_commit_timeline_diagram",
    # Git visualization functions
    "GitVisualizer",
    "visualize_git_repository",
    "create_git_tree_png",
    "create_git_tree_mermaid",
]
