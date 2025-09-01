"""
Data Visualization Module for Codomyrmex.

This module provides utilities for generating various types of plots and visualizations.

Integration:
- Uses `logging_monitoring` for all logging (ensure `setup_logging()` is called in your main app).
- Relies on `environment_setup` for environment and dependency checks (see project setup docs).

Available functions:
- create_line_plot
- create_scatter_plot
- create_bar_chart
- create_histogram
- create_pie_chart
- create_heatmap
"""

from .plotter import (
    create_line_plot,
    create_scatter_plot,
    create_bar_chart,
    create_histogram,
    create_pie_chart,
    create_heatmap,
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