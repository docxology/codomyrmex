# Data Visualization Documentation

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

Charts, graphs, and data visualization utilities.

## Key Features

- **Charts** — Line, bar, pie charts
- **Export** — PNG, SVG, HTML
- **Interactive** — Tooltip, zoom
- **Dashboards** — Multi-chart layouts

## Quick Start

```python
from codomyrmex.data_visualization import Chart

chart = Chart(type="line")
chart.add_data(x=[1, 2, 3], y=[10, 20, 15])
chart.title = "Sales Over Time"
chart.export("chart.png")
```

## Directory Contents

| File | Description |
|------|-------------|
| `README.md` | This file |
| `SPEC.md` | Technical specification |

## Navigation

- **Source**: [src/codomyrmex/data_visualization/](../../../src/codomyrmex/data_visualization/)
- **Parent**: [Modules](../README.md)
