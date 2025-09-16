"""
Data Visualization Module for Codomyrmex.

This module provides comprehensive utilities for generating various types of plots,
visualizations, and interactive dashboards.

Integration:
- Uses `logging_monitoring` for all logging (ensure `setup_logging()` is called in your main app).
- Relies on `environment_setup` for environment and dependency checks (see project setup docs).

Available functions:
- create_line_plot: Basic line plot creation
- create_scatter_plot: Basic scatter plot creation
- create_bar_chart: Basic bar chart creation
- create_histogram: Basic histogram creation
- create_pie_chart: Basic pie chart creation
- create_heatmap: Basic heatmap creation
- create_advanced_line_plot: Advanced line plot with styling
- create_advanced_scatter_plot: Advanced scatter plot with styling
- create_advanced_bar_chart: Advanced bar chart with styling
- create_advanced_histogram: Advanced histogram with styling
- create_advanced_heatmap: Advanced heatmap with styling
- create_advanced_dashboard: Multi-panel dashboard creation
- get_available_styles: Get available chart styles
- get_available_palettes: Get available color palettes
- get_available_plot_types: Get available plot types

Data structures:
- AdvancedPlotter: Main advanced plotting class
- PlotConfig: Configuration for plot generation
- DataPoint: Individual data point for plotting
- Dataset: Dataset for plotting
- PlotType: Types of plots available
- ChartStyle: Chart styling options
- ColorPalette: Color palette options
"""

from .plotter import (
    create_line_plot,
    create_scatter_plot,
    create_bar_chart,
    create_histogram,
    create_pie_chart,
    create_heatmap,
)

from .advanced_plotter import (
    AdvancedPlotter,
    create_advanced_line_plot,
    create_advanced_scatter_plot,
    create_advanced_bar_chart,
    create_advanced_histogram,
    create_advanced_heatmap,
    create_advanced_dashboard,
    get_available_styles,
    get_available_palettes,
    get_available_plot_types,
    PlotConfig,
    DataPoint,
    Dataset,
    PlotType,
    ChartStyle,
    ColorPalette,
)

from .mermaid_generator import (
    MermaidDiagramGenerator,
    create_git_branch_diagram,
    create_git_workflow_diagram,
    create_repository_structure_diagram,
    create_commit_timeline_diagram,
)

from .git_visualizer import (
    GitVisualizer,
    visualize_git_repository,
    create_git_tree_png,
    create_git_tree_mermaid,
)

__all__ = [
    # Core plotting functions
    'create_line_plot',
    'create_scatter_plot',
    'create_bar_chart',
    'create_histogram',
    'create_pie_chart',
    'create_heatmap',
    # Advanced plotting functions
    'AdvancedPlotter',
    'create_advanced_line_plot',
    'create_advanced_scatter_plot',
    'create_advanced_bar_chart',
    'create_advanced_histogram',
    'create_advanced_heatmap',
    'create_advanced_dashboard',
    'get_available_styles',
    'get_available_palettes',
    'get_available_plot_types',
    # Data structures
    'PlotConfig',
    'DataPoint',
    'Dataset',
    'PlotType',
    'ChartStyle',
    'ColorPalette',
    # Mermaid diagram functions
    'MermaidDiagramGenerator',
    'create_git_branch_diagram',
    'create_git_workflow_diagram',
    'create_repository_structure_diagram',
    'create_commit_timeline_diagram',
    # Git visualization functions
    'GitVisualizer',
    'visualize_git_repository',
    'create_git_tree_png',
    'create_git_tree_mermaid',
] 