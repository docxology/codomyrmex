# Codomyrmex Agents - src/codomyrmex/cerebrum/visualization

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Purpose

Visualization module for the CEREBRUM cognitive framework. Provides enhanced visualizations for Bayesian networks, case similarity analysis, inference results, and belief evolution. Built on matplotlib with theme support, network layouts, and chart utilities. This module enables visual inspection and presentation of cognitive model structures and reasoning outcomes.

## Active Components

- `core.py` - Main visualizers for models, cases, and inference (ModelVisualizer, CaseVisualizer, InferenceVisualizer)
- `base.py` - Base visualizer classes and utilities (BaseVisualizer, BaseNetworkVisualizer, BaseChartVisualizer, BaseHeatmapVisualizer)
- `theme.py` - Visualization theming system (VisualizationTheme, color palettes, fonts)
- `composition.py` - Composite visualization builders (dashboards, multi-panel layouts)
- `concordance.py` - Concordance analysis visualizations (comparison matrices)

## Key Classes

### ModelVisualizer (core.py)
Visualizes Bayesian networks and model structures:
- `visualize_network()`: Render Bayesian network as directed graph
  - Supports hierarchical, spring, and kamada_kawai layouts
  - Node sizing by degree, betweenness, or pagerank metrics
  - Edge styling with arrows and connection curves
- `visualize_inference_results()`: Bar charts of posterior distributions
  - Color gradient based on probability values
  - Reference line for uniform distribution
  - Value labels and legend support

### CaseVisualizer (core.py)
Visualizes case similarity and retrieval results:
- `plot_case_similarity()`: Horizontal bar chart of similarity scores
  - Color gradient from low to high similarity
  - Configurable similarity threshold line
  - Value labels on each bar
- `plot_case_features()`: Compare case features across multiple cases
  - Grouped bar charts by feature
  - Theme-consistent styling

### InferenceVisualizer (core.py)
Visualizes inference results and belief evolution:
- `plot_inference_results()`: Delegates to ModelVisualizer
- `plot_belief_evolution()`: Line plot of belief changes over time
  - Multiple state probabilities tracked
  - Markers for each time step
  - Legend with state names

### BaseVisualizer (base.py)
Abstract base class for all visualizers:
- Theme-aware figure and axes creation
- Title and label formatting utilities
- Figure saving with configurable DPI and format
- Requires matplotlib availability

### BaseNetworkVisualizer (base.py)
Base class for network/graph visualizations:
- `get_node_colors()`: Color nodes by attribute (status, part, etc.)
- `get_node_sizes()`: Size nodes by importance metric
- `get_edge_widths()`: Width edges by weight attribute
- `apply_layout()`: Apply spring, circular, hierarchical, or kamada_kawai layouts

### BaseChartVisualizer (base.py)
Base class for chart visualizations:
- `get_color_for_value()`: Map values to colormap colors
- `add_value_labels()`: Add labels on top of bars
- `add_reference_line()`: Add horizontal or vertical reference lines

### BaseHeatmapVisualizer (base.py)
Base class for heatmap visualizations:
- `create_heatmap()`: Render 2D array with row/column labels
- Configurable colormap and colorbar
- Theme-consistent axis styling

### VisualizationTheme (theme.py)
Configurable theme for consistent styling:
- Color palettes (primary, accent, status colors)
- Font settings (sizes, weights, families)
- Figure defaults (size, DPI, padding)
- Axis formatting utilities

## Operating Contracts

- Maintain alignment between code, documentation, and configured workflows
- matplotlib is required; VisualizationError raised if unavailable
- networkx is required for network visualizations
- Theme is applied to all axes automatically
- Figures are closed after saving to prevent memory leaks
- Ensure Model Context Protocol interfaces remain available for sibling agents
- Record outcomes in shared telemetry and update TODO queues when necessary

## Signposting

- **Core Module**: `../core/` - ReasoningResult and Model classes to visualize
- **Inference Module**: `../inference/` - BayesianNetwork and Distribution to render
- **FPF Integration**: `../fpf/` - Uses visualizers for CEREBRUM-FPF analysis
- **Parent Directory**: [cerebrum](../README.md) - CEREBRUM framework documentation
- **Project Root**: ../../../../README.md - Main project documentation
