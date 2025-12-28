# Data Visualization Examples

Demonstrates creating charts and visualizations using the Codomyrmex Data Visualization module.

## Overview

Create various types of charts and plots including bar charts, line plots, scatter plots, histograms, and pie charts.

## Examples

### Basic Usage (`example_basic.py`)

- Create bar charts
- Create line plots
- Create scatter plots
- Save visualizations to files

**Tested Methods:**
- `create_bar_chart()` - Create bar chart from dict data
- `create_line_plot()` - Create line plot from x/y data
- `create_scatter_plot()` - Create scatter plot

## Configuration

```yaml
data:
  bar_chart: {...}    # Data for bar chart
  line_plot: {...}    # Data for line plot
  scatter_plot: {...} # Data for scatter plot

visualization:
  output_dir: output/visualizations
  format: png
  dpi: 150
```

## Running

```bash
cd examples/data_visualization
python example_basic.py
```

Check the `output/visualizations/` directory for generated charts.

## Related Documentation

- [Module README](../../src/codomyrmex/data_visualization/README.md)
- [Unit Tests](../../testing/unit/test_data_visualization.py)

