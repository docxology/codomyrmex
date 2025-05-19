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

__all__ = [
    'create_line_plot',
    'create_scatter_plot',
    'create_bar_chart',
    'create_histogram',
    'create_pie_chart',
    'create_heatmap',
] 