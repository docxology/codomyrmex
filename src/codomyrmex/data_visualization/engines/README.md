# Engines Submodule

Core plotting engines and utilities for data visualization.

## Overview

This submodule provides the foundational plotting engines that power all chart types.

## Components

- `plotter.py` - Base plotter class
- `advanced_plotter.py` - Advanced plotting with multi-axis support
- `plot_utils.py` - Utility functions for plot configuration

## Usage

```python
from codomyrmex.data_visualization.engines import Plotter, configure_plot

plotter = Plotter()
plotter.create_figure(figsize=(10, 6))
configure_plot(title="My Chart", xlabel="X", ylabel="Y")
```
