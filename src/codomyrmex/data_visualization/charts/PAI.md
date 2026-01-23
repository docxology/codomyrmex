# Charts Submodule - Programmatic AI Instructions

## Module Identity

- **Path**: `codomyrmex.data_visualization.charts`
- **Purpose**: Chart type implementations for visualization

## Quick Reference

### Imports

```python
from codomyrmex.data_visualization.charts import (
    BarChart, LinePlot, PieChart, Histogram, ScatterPlot,
    create_bar_chart, create_line_plot
)
```

### Common Patterns

```python
# Create chart
chart = create_bar_chart(data=[10, 20, 30], labels=["A", "B", "C"])

# Render to file
chart.render("output.png")

# Configure options
chart.configure(title="Sales", color_scheme="viridis")
```

## AI Agent Notes

- Prefer factory functions over direct class instantiation
- All charts support PNG, SVG, PDF export
- Use themes/ submodule for consistent styling
