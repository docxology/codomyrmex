# Engines Submodule - Agent Instructions

## Purpose

Core plotting engines providing the foundation for all visualizations.

## Key Files

- `plotter.py` - Base Plotter class with core functionality
- `advanced_plotter.py` - Multi-axis and complex layouts
- `plot_utils.py` - Utilities for configuration and export

## Agent Guidelines

- Use Plotter for simple single-axis plots
- Use AdvancedPlotter for multi-panel or complex layouts
- Always call configure_plot() before rendering
- Use save_figure() for consistent export behavior
