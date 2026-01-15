# Data Visualization

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Overview
The `data_visualization` module serves as the presentation layer for Codomyrmex analytics. It provides a comprehensive suite of tools for generating static charts, interactive plots, and structural diagrams. By abstracting over libraries like Matplotlib and Mermaid.js, it ensures a consistent visual language across all project outputs, from code metrics reports to audit visualizations.

## Key Features
- **Standardized Charting**: Reusable classes for Bar, Line, Scatter, Pie, and Histogram plots ensure visual consistency.
- **Advanced Plotting**: The `AdvancedPlotter` class supports complex multi-axis and sub-plot configurations.
- **Diagram Generation**: The `MermaidGenerator` creates flowcharts, sequence diagrams, and class diagrams programmatically.
- **Source Code Visualization**: The `GitVisualizer` maps repository history and structure into visual formats.

## Quick Start

```python
from codomyrmex.data_visualization import BarChart, MermaidGenerator

# Create a simple bar chart
chart = BarChart(title="Agent Performance")
chart.add_series([10, 20, 15], labels=["A", "B", "C"])
chart.save("performance.png")

# Generate a flowchart
mermaid = MermaidGenerator()
mermaid.add_node("Start", "A")
mermaid.add_node("Process", "B")
mermaid.add_link("A", "B", label="initiates")
print(mermaid.render())
```

## Module Structure

### Plotting Primitives
- `bar_chart.py`: Categorical data visualization.
- `line_plot.py`: Time-series and trend visualization.
- `scatter_plot.py`: Correlation analysis.
- `histogram.py`: Distribution analysis.
- `pie_chart.py`: Proportional data visualization.

### Advanced Tools
- `advanced_plotter.py`: Composite visualizations.
- `mermaid_generator.py`: Text-to-diagram generation.
- `git_visualizer.py`: Repository analytics.
- `plot_utils.py`: Common styling and helper functions.

## Navigation Links
- **Technical Documentation**: [AGENTS.md](AGENTS.md)
- **Functional Specification**: [SPEC.md](SPEC.md)
- **API Specification**: [API_SPECIFICATION.md](API_SPECIFICATION.md)
- **Usage Examples**: [USAGE_EXAMPLES.md](USAGE_EXAMPLES.md)
- **📁 Parent Directory**: [codomyrmex](../README.md)
- **🏠 Project Root**: [README](../../../README.md)
