# Codomyrmex Agents — src/codomyrmex/data_visualization

## Signposting
- **Parent**: [codomyrmex](../AGENTS.md)
- **Self**: [Agents](AGENTS.md)
- **Children**:
    - [docs](docs/AGENTS.md)
    - [tests](tests/AGENTS.md)
- **Key Artifacts**:
    - [Functional Spec](SPEC.md)
    - [Human Readme](README.md)

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Purpose
Charts and plots generation for data visualization. Provides comprehensive visualization capabilities including various chart types (bar, line, scatter, pie, histogram), advanced plotting features, Mermaid diagram generation, and Git visualization. Supports multiple output formats and integration with data analysis workflows.

## Active Components
- `API_SPECIFICATION.md` – Detailed API specification
- `CHANGELOG.md` – Version history
- `MCP_TOOL_SPECIFICATION.md` – MCP tool specification
- `README.md` – Project file
- `SECURITY.md` – Security considerations
- `SPEC.md` – Project file
- `USAGE_EXAMPLES.md` – Usage examples
- `__init__.py` – Module exports and public API
- `advanced_plotter.py` – Advanced plotting features
- `bar_chart.py` – Bar chart generation
- `docs/` – Directory containing docs components
- `git_visualizer.py` – Git visualization utilities
- `histogram.py` – Histogram generation
- `line_plot.py` – Line plot generation
- `mermaid_generator.py` – Mermaid diagram generation
- `pie_chart.py` – Pie chart generation
- `plot_utils.py` – Plotting utilities
- `plotter.py` – Main plotting interface
- `requirements.txt` – Project file
- `scatter_plot.py` – Scatter plot generation
- `tests/` – Directory containing tests components

## Key Classes and Functions

### Plotter (`plotter.py`)
- `Plotter()` – Main plotting interface
- `create_plot(data: pd.DataFrame, plot_type: str, **kwargs) -> str` – Create a plot and return file path
- `save_visualization(fig: Any, filepath: str) -> None` – Save visualization to file

### Chart Generators
- `create_bar_chart(data: pd.DataFrame, x: str, y: str, **kwargs) -> str` – Create bar chart
- `create_line_plot(data: pd.DataFrame, x: str, y: str, **kwargs) -> str` – Create line plot
- `create_scatter_plot(data: pd.DataFrame, x: str, y: str, **kwargs) -> str` – Create scatter plot
- `create_pie_chart(data: pd.DataFrame, labels: str, values: str, **kwargs) -> str` – Create pie chart
- `create_histogram(data: pd.Series, bins: int = 10, **kwargs) -> str` – Create histogram

### MermaidGenerator (`mermaid_generator.py`)
- `MermaidGenerator()` – Mermaid diagram generation
- `generate_flowchart(nodes: list, edges: list, **kwargs) -> str` – Generate flowchart diagram
- `generate_sequence_diagram(participants: list, messages: list, **kwargs) -> str` – Generate sequence diagram
- `generate_class_diagram(classes: list, relationships: list, **kwargs) -> str` – Generate class diagram

### GitVisualizer (`git_visualizer.py`)
- `GitVisualizer()` – Git visualization utilities
- `visualize_commit_history(repo_path: str, **kwargs) -> str` – Visualize commit history
- `visualize_branch_structure(repo_path: str, **kwargs) -> str` – Visualize branch structure

### AdvancedPlotter (`advanced_plotter.py`)
- `AdvancedPlotter()` – Advanced plotting features
- `create_multi_panel_plot(panels: list, layout: str = "grid") -> str` – Create multi-panel plot
- `create_interactive_plot(data: pd.DataFrame, plot_type: str, **kwargs) -> str` – Create interactive plot

## Operating Contracts
- Maintain alignment between code, documentation, and configured workflows.
- Ensure Model Context Protocol interfaces remain available for sibling agents.
- Record outcomes in shared telemetry and update TODO queues when necessary.

## Navigation Links
- **Human Documentation**: [README.md](README.md)
- **Functional Specification**: [SPEC.md](SPEC.md)
- **📁 Parent Directory**: [codomyrmex](../README.md) - Parent directory documentation
- **🏠 Project Root**: [README](../../../README.md) - Main project documentation