# Charts -- Technical Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

Eight chart types built on matplotlib with a dual API: functional factory functions (`create_*`) for quick usage and dataclass-backed classes (`BarChart`, `ScatterPlot`, etc.) for object-oriented composition. Shared utilities in `plot_utils.py` handle saving, theming, and color palettes.

## Architecture

Each chart module follows the same pattern:

1. A `create_<chart>()` factory function that creates a matplotlib figure, renders the chart, optionally saves/shows it, and returns the `Figure` object (or `None` on invalid input).
2. A class wrapper (e.g., `BarChart`) with `__init__` for configuration, `render()` to delegate to the factory, `save()` and `show()` convenience methods, and a `data` property returning `{"x": ..., "y": ...}`.

Three factory functions (`create_bar_chart`, `create_line_plot`, `create_pie_chart`) are decorated with `@mcp_tool()` for MCP auto-discovery.

## Key Functions

### `plot_utils.py`

| Function | Parameters | Returns | Description |
|----------|-----------|---------|-------------|
| `save_plot` | `fig, output_path: str, dpi=150, transparent=False` | `bool` | Save figure to file, format detected from extension |
| `apply_theme_to_axes` | `ax, theme_name` | `Axes` | Apply a ThemeName to matplotlib axes |
| `get_color_palette` | `n_colors: int` | `list[str]` | Return a list of hex color codes, cycling if needed |
| `apply_common_aesthetics` | `ax, title, x_label, y_label` | `Axes` | Remove top/right spines, add grid, set labels |
| `configure_plot` | `fig, ax, theme_name=None, **kwargs` | `(fig, ax)` | Combine theme and aesthetics in one call |

### `create_bar_chart()`

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `categories` | `list` | -- | Category labels |
| `values` | `list` | -- | Numeric values per category |
| `horizontal` | `bool` | `False` | Horizontal bar orientation |
| `bar_color` | `str` | `"skyblue"` | Bar fill color |
| `theme` | `ThemeName` | `None` | Optional theme to apply |

### `create_scatter_plot()`

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `x_data` | `list` | -- | X-axis values |
| `y_data` | `list` | -- | Y-axis values |
| `dot_size` | `int` | `20` | Marker size |
| `dot_color` | `str` | `"blue"` | Marker color |
| `alpha` | `float` | `0.7` | Transparency (0-1) |

### `create_line_plot()`

Supports multiple lines when `y_data` is a list of lists and `line_labels` provides legend entries.

### `create_heatmap()`

Accepts a 2D list, optional axis labels, colormap name, annotation toggle, and format string.

## Dependencies

- **Internal**: `logging_monitoring.core.logger_config`, `model_context_protocol.decorators`, `data_visualization.themes` (optional)
- **External**: `matplotlib >= 3.5.0`, `numpy >= 1.21.0`

## Constraints

- Input validation returns `None` and logs a warning rather than raising exceptions.
- `DEFAULT_FIGURE_SIZE` is `(10, 6)` across all chart types.
- Zero-mock: real matplotlib rendering only; `NotImplementedError` for unimplemented paths.
- All chart functions call `plt.close(fig)` when `show_plot=False` to prevent memory leaks.

## Error Handling

- Empty or mismatched data logs a warning and returns `None`.
- `save_plot()` catches all exceptions, logs the error, and returns `False`.
- Theme application failure is logged at debug level and silently ignored.
