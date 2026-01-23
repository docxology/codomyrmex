# Engines Submodule - Programmatic AI Instructions

## Module Identity

- **Path**: `codomyrmex.data_visualization.engines`
- **Purpose**: Core plotting engines

## Quick Reference

```python
from codomyrmex.data_visualization.engines import Plotter, AdvancedPlotter

# Basic usage
plotter = Plotter()
fig = plotter.create_figure((10, 6))
plotter.render("output.png")

# Advanced multi-panel
adv = AdvancedPlotter(rows=2, cols=2)
adv.add_subplot(0, 0, data, "line")
adv.render("grid.png")
```

## AI Notes

- Plotter is the base for all chart types
- AdvancedPlotter enables complex layouts
- Theme integration via apply_style()
