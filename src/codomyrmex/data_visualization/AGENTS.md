# Codomyrmex Agents — src/codomyrmex/data_visualization

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Purpose

The Data Visualization module provides comprehensive charting, plotting, and diagram generation capabilities for Codomyrmex. It supports statistical visualizations using matplotlib/seaborn, Mermaid diagram generation for documentation and workflows, and specialized Git repository visualizations for branch trees, commit timelines, and repository analysis dashboards.

## Active Components

### Core Plotting Infrastructure

- `advanced_plotter.py` - Advanced plotting class with comprehensive visualization capabilities
  - Key Classes: `AdvancedPlotter`, `PlotConfig`, `DataPoint`, `Dataset`
  - Key Enums: `PlotType`, `ChartStyle`, `ColorPalette`
  - Key Functions: `create_advanced_line_plot()`, `create_advanced_scatter_plot()`, `create_advanced_bar_chart()`, `create_advanced_histogram()`, `create_advanced_heatmap()`, `create_advanced_dashboard()`

- `plotter.py` - Main plotter interface consolidating plotting functions
  - Key Functions: `create_heatmap()`, `save_plot()`

- `plot_utils.py` - Utility functions for plotting and logging
  - Key Functions: `save_plot()`, `apply_common_aesthetics()`, `get_codomyrmex_logger()`

### Basic Chart Types

- `line_plot.py` - Line plot creation
- `scatter_plot.py` - Scatter plot creation
- `bar_chart.py` - Bar chart generation
- `histogram.py` - Histogram generation
- `pie_chart.py` - Pie chart generation

### Mermaid Diagram Generation

- `mermaid_generator.py` - Mermaid diagram generation for documentation and workflows
  - Key Classes: `MermaidDiagramGenerator`
  - Key Functions: `create_git_branch_diagram()`, `create_git_workflow_diagram()`, `create_repository_structure_diagram()`, `create_commit_timeline_diagram()`

### Git Visualization

- `git_visualizer.py` - Git-specific visualizations integrating with git_operations
  - Key Classes: `GitVisualizer`
  - Key Functions: `visualize_git_repository()`, `create_git_tree_png()`, `create_git_tree_mermaid()`

## Key Classes and Functions

| Class/Function | Module | Purpose |
| :--- | :--- | :--- |
| `AdvancedPlotter` | advanced_plotter | Main plotting class with multi-type chart support |
| `PlotConfig` | advanced_plotter | Configuration dataclass for plot generation |
| `DataPoint` | advanced_plotter | Individual data point representation |
| `Dataset` | advanced_plotter | Dataset container for plotting |
| `PlotType` | advanced_plotter | Enum of available plot types (line, scatter, bar, etc.) |
| `ChartStyle` | advanced_plotter | Enum of styling options (minimal, dark, whitegrid, etc.) |
| `ColorPalette` | advanced_plotter | Enum of color palette options |
| `MermaidDiagramGenerator` | mermaid_generator | Generator for Mermaid diagrams |
| `GitVisualizer` | git_visualizer | Comprehensive Git visualization class |
| `create_figure()` | AdvancedPlotter | Create matplotlib figure with subplots |
| `plot_line()` | AdvancedPlotter | Create line plot |
| `plot_scatter()` | AdvancedPlotter | Create scatter plot |
| `plot_bar()` | AdvancedPlotter | Create bar chart |
| `plot_histogram()` | AdvancedPlotter | Create histogram |
| `plot_heatmap()` | AdvancedPlotter | Create heatmap |
| `plot_box()` | AdvancedPlotter | Create box plot |
| `plot_violin()` | AdvancedPlotter | Create violin plot |
| `plot_correlation()` | AdvancedPlotter | Create correlation heatmap |
| `create_dashboard()` | AdvancedPlotter | Create multi-panel dashboard |
| `visualize_git_tree_png()` | GitVisualizer | Create PNG Git tree visualization |
| `visualize_git_tree_mermaid()` | GitVisualizer | Create Mermaid Git tree diagram |
| `visualize_commit_activity_png()` | GitVisualizer | Create commit activity chart |
| `visualize_repository_summary_png()` | GitVisualizer | Create repository dashboard |
| `create_comprehensive_git_report()` | GitVisualizer | Generate full Git analysis report |

## Operating Contracts

1. **Logging**: All components use `logging_monitoring` for structured logging via `get_codomyrmex_logger()`
2. **Performance Monitoring**: Plotting functions are decorated with `@monitor_performance` for execution tracking
3. **Dependencies**: Requires matplotlib, seaborn, numpy, and pandas; falls back gracefully if unavailable
4. **Git Integration**: Git visualizations require `git_operations` module for repository data
5. **Output Formats**: Supports PNG, PDF, SVG for matplotlib plots; .mmd files for Mermaid diagrams
6. **Configuration**: Plot styling configurable via `PlotConfig` dataclass and enum options

## Integration Points

- **logging_monitoring** - All plotting functions log via centralized logger
- **performance** - Uses `monitor_performance` decorator for execution tracking
- **git_operations** - GitVisualizer integrates with git commands for repository data
- **environment_setup** - Dependency checking at application startup

## Signposting

### Document Hierarchy

- **Self**: [AGENTS.md](AGENTS.md)
- **Parent**: [src/codomyrmex/AGENTS.md](../AGENTS.md)
- **Project Root**: [../../../AGENTS.md](../../../AGENTS.md)

### Sibling Modules

| Module | AGENTS.md | Purpose |
| :--- | :--- | :--- |
| git_operations | [../git_operations/AGENTS.md](../git_operations/AGENTS.md) | Git repository operations |
| logging_monitoring | [../logging_monitoring/AGENTS.md](../logging_monitoring/AGENTS.md) | Logging infrastructure |
| performance | [../performance/AGENTS.md](../performance/AGENTS.md) | Performance optimization |
| documentation | [../documentation/AGENTS.md](../documentation/AGENTS.md) | Documentation generation |

### Related Documentation

- [README.md](README.md) - User documentation
- [API_SPECIFICATION.md](API_SPECIFICATION.md) - API documentation
- [SPEC.md](SPEC.md) - Functional specification
- [USAGE_EXAMPLES.md](USAGE_EXAMPLES.md) - Usage examples
- [MCP_TOOL_SPECIFICATION.md](MCP_TOOL_SPECIFICATION.md) - MCP tool specifications
