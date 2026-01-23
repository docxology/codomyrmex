# Codomyrmex Agents - src/codomyrmex/fpf/visualization

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Purpose

Visualization module for FPF (First Principles Framework) specifications. Provides Mermaid diagram generation for pattern hierarchies and dependencies, comprehensive report generation, pattern cards, and NetworkX-based graph visualizations with matplotlib. This module enables visual exploration and presentation of FPF structure.

## Active Components

- `visualizer.py` - Mermaid diagrams and reports (FPFVisualizer)
- `graph_generator.py` - NetworkX graph generation and layouts (GraphGenerator)
- `term_analyzer.py` - Term visualization utilities
- `visualizer_png.py` - PNG export utilities

## Key Classes

### FPFVisualizer (visualizer.py)
Visualizer for FPF specifications:
- `visualize_pattern_hierarchy()`: Generate Mermaid diagram of pattern hierarchy
  - Groups patterns by part
  - Creates nodes with truncated titles (max 30 chars)
  - Adds edges for builds_on relationships
  - Returns Mermaid graph TD string
- `visualize_dependencies()`: Generate Mermaid diagram of all dependencies
  - Creates nodes for all patterns
  - Different arrow styles by relationship type:
    - `-->` for builds_on
    - `-.->` for prerequisite_for
    - `==>` for coordinates_with
  - Returns Mermaid graph LR string
- `generate_report()`: Create comprehensive markdown report
  - Patterns grouped by status (Stable, Draft, Stub, New)
  - Patterns grouped by part
  - Top 20 concepts with definitions
  - Writes to output file
- `create_pattern_card()`: Generate markdown card for single pattern
  - Status, keywords, dependencies, section previews

### GraphGenerator (graph_generator.py)
Generator for graph visualizations using NetworkX and matplotlib:
- `create_pattern_dependency_graph()`: Create NetworkX DiGraph
  - Nodes with title, status, part attributes
  - Edges for builds_on and prerequisite_for relationships
- `create_term_cooccurrence_graph()`: Create NetworkX Graph
  - Nodes for terms, edges weighted by co-occurrence count
  - Filters by minimum weight threshold
- `create_concept_relationship_graph()`: Create concept graph
  - Nodes for concepts with type and pattern_id
  - Edges between concepts sharing patterns

Layout methods:
- `apply_hierarchical_layout()`: Graphviz dot layout (fallback: spring)
- `apply_force_directed_layout()`: Spring layout with configurable k and iterations
- `apply_circular_layout()`: Circular node arrangement
- `apply_tree_layout()`: Tree layout from optional root node

Styling methods:
- `get_node_colors_by_attribute()`: Color nodes by status or part
  - Status colors: Stable=green, Draft=orange, Stub=gray, New=blue
  - Part colors: from matplotlib Set3 colormap
- `get_node_sizes_by_importance()`: Size nodes by centrality metric
  - Metrics: degree, betweenness, pagerank
  - Scales to 100-2000 range

Configuration:
- `figsize`: Figure dimensions in inches (default: 12x8)
- `dpi`: Output resolution (default: 300)

## Operating Contracts

- Maintain alignment between code, documentation, and configured workflows
- FPFVisualizer generates Mermaid markdown strings (rendering done externally)
- GraphGenerator requires NetworkX and matplotlib
- Graphviz layout falls back to spring layout if unavailable
- Node titles are truncated to 30 characters in diagrams
- Report generation creates parent directories automatically
- Ensure Model Context Protocol interfaces remain available for sibling agents
- Record outcomes in shared telemetry and update TODO queues when necessary

## Signposting

- **Core Module**: `../core/` - FPFSpec, Pattern models for visualization
- **Analysis Module**: `../analysis/` - FPFAnalyzer, TermAnalyzer provide data for graphs
- **IO Module**: `../io/` - FPFExporter exports alongside visualizations
- **CEREBRUM Visualization**: `../../cerebrum/visualization/` - Enhanced visualizers used by CEREBRUM-FPF
- **Parent Directory**: [fpf](../README.md) - FPF package documentation
- **Project Root**: ../../../../README.md - Main project documentation
