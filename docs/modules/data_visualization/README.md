# Data Visualization Module Documentation

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

Data Visualization Module for Codomyrmex.

## Key Features

- **ChartStyle** — Fallback chart style enum.
- **ColorPalette** — Fallback color palette enum.
- **PlotType** — Fallback plot type enum.
- `get_available_styles()` — Get available chart styles.
- `get_available_palettes()` — Get available color palettes.
- `get_available_plot_types()` — Get available plot types.

## Submodules

| Submodule | Description |
|-----------|-------------|
| `charts` | Charts submodule for data_visualization. |
| `engines` | Engines submodule for data_visualization. |
| `git` | Git visualization submodule for data_visualization. |
| `mermaid` | Mermaid diagram generation utilities. |
| `themes` | Theme definitions for data visualization. |

## Quick Start

```python
from codomyrmex.data_visualization import ChartStyle, ColorPalette, PlotType

# Initialize
instance = ChartStyle()
```


## Installation

```bash
uv pip install codomyrmex
```

## API Reference

### Classes

| Class | Description |
|-------|-------------|
| `ChartStyle` | Fallback chart style enum. |
| `ColorPalette` | Fallback color palette enum. |
| `PlotType` | Fallback plot type enum. |

### Functions

| Function | Description |
|----------|-------------|
| `get_available_styles()` | Get available chart styles. |
| `get_available_palettes()` | Get available color palettes. |
| `get_available_plot_types()` | Get available plot types. |

## Directory Contents

| File | Description |
|------|-------------|
| `README.md` | This documentation |
| `AGENTS.md` | Agent coordination guide |
| `SPEC.md` | Technical specification |
| `tutorials/` | Tutorials |


## Testing

```bash
uv run python -m pytest src/codomyrmex/tests/ -k data_visualization -v
```

## Navigation

- **Source**: [src/codomyrmex/data_visualization/](../../../src/codomyrmex/data_visualization/)
- **Parent**: [Modules](../README.md)
