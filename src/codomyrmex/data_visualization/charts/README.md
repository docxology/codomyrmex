# Charts Submodule

Chart type implementations for data visualization.

## Overview

This submodule contains specific chart type implementations including bar charts, line plots, pie charts, histograms, and scatter plots.

## Components

- `bar_chart.py` - Bar chart implementation
- `line_plot.py` - Line plot implementation  
- `pie_chart.py` - Pie chart implementation
- `histogram.py` - Histogram implementation
- `scatter_plot.py` - Scatter plot implementation

## Usage

```python
from codomyrmex.data_visualization.charts import BarChart, create_bar_chart

chart = create_bar_chart(data, labels)
chart.render()
```

## Dependencies

- matplotlib
- numpy
