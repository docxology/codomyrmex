# data_visualization

## Signposting
- **Parent**: [codomyrmex](../README.md)
- **Children**:
    - [docs](docs/README.md)
    - [tests](tests/README.md)
- **Key Artifacts**:
    - [Agent Guide](AGENTS.md)
    - [Functional Spec](SPEC.md)

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Overview

Charts and plots generation for data visualization. Provides comprehensive visualization capabilities including various chart types (bar, line, scatter, pie, histogram), advanced plotting features, Mermaid diagram generation, and Git visualization. Supports multiple output formats and integration with data analysis workflows.

## Directory Contents
- `API_SPECIFICATION.md` – File
- `CHANGELOG.md` – File
- `MCP_TOOL_SPECIFICATION.md` – File
- `README.md` – File
- `SECURITY.md` – File
- `SPEC.md` – File
- `USAGE_EXAMPLES.md` – File
- `__init__.py` – File
- `advanced_plotter.py` – File
- `bar_chart.py` – File
- `docs/` – Subdirectory
- `git_visualizer.py` – File
- `histogram.py` – File
- `line_plot.py` – File
- `mermaid_generator.py` – File
- `pie_chart.py` – File
- `plot_utils.py` – File
- `plotter.py` – File
- `requirements.txt` – File
- `scatter_plot.py` – File
- `tests/` – Subdirectory

## Navigation
- **Technical Documentation**: [AGENTS.md](AGENTS.md)
- **Functional Specification**: [SPEC.md](SPEC.md)
- **Parent Directory**: [codomyrmex](../README.md)
- **Project Root**: [README](../../../README.md)

## Getting Started

To use this module in your project, import the necessary components:

```python
from codomyrmex.data_visualization import (
    create_line_plot,
    create_bar_chart,
    create_pie_chart,
    create_scatter_plot,
    create_histogram,
    AdvancedPlotter,
    MermaidDiagramGenerator,
    GitVisualizer,
)

# Create a line plot
create_line_plot(
    data=[1, 2, 3, 4, 5],
    labels=["A", "B", "C", "D", "E"],
    output_path="line_plot.png"
)

# Create a bar chart
create_bar_chart(
    data={"Jan": 10, "Feb": 15, "Mar": 12},
    title="Monthly Sales",
    output_path="bar_chart.png"
)

# Use advanced plotter
plotter = AdvancedPlotter()
dashboard = plotter.create_dashboard(
    plots=[
        {"type": "line", "data": [1, 2, 3]},
        {"type": "bar", "data": {"A": 10, "B": 20}}
    ],
    output_path="dashboard.png"
)

# Generate Mermaid diagram
mermaid = MermaidDiagramGenerator()
diagram = mermaid.create_git_branch_diagram(repo_path=".")
print(diagram)

# Visualize Git repository
git_viz = GitVisualizer()
git_viz.visualize_git_repository("src/", output_path="git_tree.png")
```

