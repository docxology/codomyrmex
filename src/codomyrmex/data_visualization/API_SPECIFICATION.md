# Data Visualization - API Specification

## Introduction

This document specifies the Application Programming Interface (API) for the Data Visualization module. The primary purpose of this API is to provide a set of Python functions for generating various types of common plots and visualizations programmatically, primarily using Matplotlib and Seaborn as backend engines.

The API is designed to be straightforward, allowing users to quickly generate visualizations with sensible defaults, while also offering customization options for titles, labels, colors, output paths, and more.

## Prerequisites & Initialization

- Ensure the `logging_monitoring` module is available and `setup_logging()` has been called at the application startup (or before using any visualization functions) for consistent logging of visualization activities.
- Dependencies such as `matplotlib`, `seaborn`, and `numpy` must be installed. Refer to `pyproject.toml` for specific versions. It's recommended to use the `environment_setup` module or project-level scripts to verify/install dependencies.
- Python 3.7+ (or as specified by the project's root `pyproject.toml`).

## General Conventions

- **Data Inputs**: Data for plotting (e.g., `x_data`, `y_data`, `values`, `data`) is typically expected as Python lists or NumPy arrays. Specific functions will detail their exact requirements.
- **Output**: Functions can either save the plot to a file (via `output_path` or `save_path`) and/or display it interactively (via `show_plot` in `PlotConfig`). By default, plots are shown but not saved unless a path is specified.
- **Return Values**: The advanced convenience functions (`create_line_plot`, `create_scatter_plot`, `create_bar_chart`, `create_histogram`, `create_heatmap_advanced`, `create_dashboard`) return `plt.Figure` objects. The basic chart module functions (`create_heatmap`, `create_pie_chart`, `create_box_plot`, `create_area_chart`) return `None`.
- **Logging**: All public API functions integrate with the `logging_monitoring` module to log key actions, parameters, and any errors encountered.
- **Customization**: All advanced functions accept a `PlotConfig` dataclass for style, palette, figure size, and other settings. Additional Matplotlib/Seaborn kwargs are forwarded via `**kwargs`.

## Plotting Functions

All plotting functions are Python functions importable from `codomyrmex.data_visualization`. For example: `from codomyrmex.data_visualization import create_line_plot`.

### Function 1: `create_line_plot()`

When the advanced plotter engine is available (default), this is an alias for `create_advanced_line_plot`.

- **Description**: Generates a line plot using the `AdvancedPlotter`.
- **Path**: `from codomyrmex.data_visualization import create_line_plot`
- **Parameters/Arguments**:
  - `x_data` (list): X-axis data values.
  - `y_data` (list): Y-axis data values. Must match length of `x_data`.
  - `title` (str, optional): Plot title. Default: `""`.
  - `xlabel` (str, optional): X-axis label. Default: `""`.
  - `ylabel` (str, optional): Y-axis label. Default: `""`.
  - `config` (PlotConfig, optional): Plot configuration. Default: `None` (uses defaults).
  - `save_path` (str, optional): File path to save the plot. Default: `None`.
  - `**kwargs`: Forwarded to `AdvancedPlotter.plot_line()` (e.g., `label`, `color`, `linewidth`, `linestyle`, `marker`, `markersize`, `alpha`).
- **Returns/Response**: `plt.Figure` object.

### Function 2: `create_scatter_plot()`

When the advanced plotter engine is available (default), this is an alias for `create_advanced_scatter_plot`.

- **Description**: Generates a scatter plot using the `AdvancedPlotter`.
- **Path**: `from codomyrmex.data_visualization import create_scatter_plot`
- **Parameters/Arguments**:
  - `x_data` (list): X-axis data values.
  - `y_data` (list): Y-axis data values. Must match length of `x_data`.
  - `title` (str, optional): Plot title. Default: `""`.
  - `xlabel` (str, optional): X-axis label. Default: `""`.
  - `ylabel` (str, optional): Y-axis label. Default: `""`.
  - `config` (PlotConfig, optional): Plot configuration. Default: `None`.
  - `**kwargs`: Forwarded to `AdvancedPlotter.plot_scatter()` (e.g., `label`, `color`, `size`, `alpha`, `marker`).
- **Returns/Response**: `plt.Figure` object.

### Function 3: `create_bar_chart()`

When the advanced plotter engine is available (default), this is an alias for `create_advanced_bar_chart`.

- **Description**: Generates a bar chart using the `AdvancedPlotter`.
- **Path**: `from codomyrmex.data_visualization import create_bar_chart`
- **Parameters/Arguments**:
  - `x_data` (list): Category names or x-axis values.
  - `y_data` (list): Numerical values corresponding to each category.
  - `title` (str, optional): Chart title. Default: `""`.
  - `xlabel` (str, optional): X-axis label. Default: `""`.
  - `ylabel` (str, optional): Y-axis label. Default: `""`.
  - `config` (PlotConfig, optional): Plot configuration. Default: `None`.
  - `save_path` (str, optional): File path to save the chart. Default: `None`.
  - `**kwargs`: Forwarded to `AdvancedPlotter.plot_bar()` (e.g., `label`, `color`, `alpha`, `width`, `orientation`).
- **Returns/Response**: `plt.Figure` object.

### Function 4: `create_histogram()`

When the advanced plotter engine is available (default), this is an alias for `create_advanced_histogram`.

- **Description**: Generates a histogram using the `AdvancedPlotter`.
- **Path**: `from codomyrmex.data_visualization import create_histogram`
- **Parameters/Arguments**:
  - `data` (list): Numerical values from which to generate the histogram.
  - `title` (str, optional): Histogram title. Default: `""`.
  - `xlabel` (str, optional): X-axis label. Default: `""`.
  - `ylabel` (str, optional): Y-axis label. Default: `""`.
  - `config` (PlotConfig, optional): Plot configuration. Default: `None`.
  - `**kwargs`: Forwarded to `AdvancedPlotter.plot_histogram()` (e.g., `bins`, `label`, `color`, `alpha`, `density`, `cumulative`).
- **Returns/Response**: `plt.Figure` object.

### Function 5: `create_pie_chart()`

Available from the basic charts module (fallback when advanced plotter handles other chart types).

- **Description**: Generates a pie chart to show proportions.
- **Path**: `from codomyrmex.data_visualization import create_pie_chart`
- **Parameters/Arguments**:
  - `labels` (list of str): Labels for each slice of the pie.
  - `sizes` (list or np.ndarray): Numerical values representing each slice size. Values should be positive.
  - `title` (str, optional): Pie chart title. Default: `"Pie Chart"`.
  - `output_path` (str, optional): File path to save the chart. Default: `None`.
  - `show_plot` (bool, optional): If `True`, displays the chart. Default: `False`.
  - `autopct` (str or function, optional): Label format for wedges. Default: `'%1.1f%%'`.
  - `startangle` (float, optional): Rotation offset in degrees. Default: `90`.
  - `explode` (list of float, optional): Offset fraction per slice. Default: `None`.
  - `colors` (list of str, optional): Color per slice. Default: `None` (Matplotlib default).
- **Returns/Response**: None.

### Function 6: `create_heatmap()`

From the basic charts module. For an advanced version, see `create_heatmap_advanced` (alias for `create_advanced_heatmap`).

- **Description**: Generates a heatmap from a 2D data array using Seaborn.
- **Path**: `from codomyrmex.data_visualization import create_heatmap`
- **Parameters/Arguments**:
  - `data` (2D list or 2D np.ndarray): The 2D data to visualize.
  - `x_labels` (list of str, optional): Column labels. Default: `None`.
  - `y_labels` (list of str, optional): Row labels. Default: `None`.
  - `title` (str, optional): Heatmap title. Default: `"Heatmap"`.
  - `x_label` (str, optional): X-axis label. Default: `None`.
  - `y_label` (str, optional): Y-axis label. Default: `None`.
  - `cmap` (str, optional): Matplotlib colormap name. Default: `"viridis"`.
  - `colorbar_label` (str, optional): Colorbar label. Default: `None`.
  - `output_path` (str, optional): File path to save. Default: `None`.
  - `show_plot` (bool, optional): If `True`, displays the plot. Default: `False`.
  - `annot` (bool or 2D array-like, optional): Annotate cells. Default: `False`.
  - `fmt` (str, optional): Annotation format. Default: `".2f"`.
  - `linewidths` (float, optional): Cell divider line width. Default: `0`.
  - `linecolor` (str, optional): Cell divider line color. Default: `'white'`.
- **Returns/Response**: None.

### Function 7: `create_box_plot()`

- **Description**: Generates a box plot for visualizing data distribution.
- **Path**: `from codomyrmex.data_visualization import create_box_plot`
- **Parameters/Arguments**: Depends on the `BoxPlot` class from the basic charts module. Accepts data, labels, title, output_path, and show_plot parameters.
- **Returns/Response**: None.

### Function 8: `create_area_chart()`

- **Description**: Generates an area chart (filled line plot).
- **Path**: `from codomyrmex.data_visualization import create_area_chart`
- **Parameters/Arguments**: Depends on the `AreaChart` class from the basic charts module. Accepts x_data, y_data, title, output_path, and show_plot parameters.
- **Returns/Response**: None.

## AdvancedPlotter Class

The `AdvancedPlotter` class provides a stateful, composable plotting API built on Matplotlib and Seaborn.

```python
from codomyrmex.data_visualization import AdvancedPlotter, PlotConfig

plotter = AdvancedPlotter(config=PlotConfig(title="My Chart", style=ChartStyle.WHITEGRID))
plotter.plot_line([1, 2, 3], [4, 5, 6], label="Series A")
fig = plotter.finalize_plot(save_path="output.png")
```

### Constructor

```python
class AdvancedPlotter:
    def __init__(self, config: PlotConfig = None): ...
```

- `config` (PlotConfig, optional): Plot configuration. Default: `PlotConfig()` with default values.

### Key Methods

| Method | Returns | Description |
|--------|---------|-------------|
| `create_figure(subplots=(1,1), **kwargs)` | `tuple[Figure, Axes]` | Create a new figure with optional subplots |
| `plot_line(x_data, y_data, label="", color=None, linewidth=2.0, linestyle="-", marker=None, markersize=6.0, alpha=1.0, **kwargs)` | `Line2D` | Add a line to the current axes |
| `plot_scatter(x_data, y_data, label="", color=None, size=50, alpha=0.7, marker="o", **kwargs)` | `PathCollection` | Add a scatter plot |
| `plot_bar(x_data, y_data, label="", color=None, alpha=0.8, width=0.8, orientation="vertical", **kwargs)` | `BarContainer` | Add a bar chart |
| `plot_histogram(data, bins=30, label="", color=None, alpha=0.7, density=False, cumulative=False, **kwargs)` | `tuple[counts, bin_edges, patches]` | Add a histogram |
| `plot_heatmap(data, x_labels=None, y_labels=None, cmap="viridis", annot=False, fmt=".2f", cbar=True, **kwargs)` | `AxesImage` | Add a heatmap (uses Seaborn) |
| `plot_box(data, labels=None, color=None, notch=False, patch_artist=True, **kwargs)` | `dict[str, Any]` | Add a box plot |
| `plot_violin(data, labels=None, color=None, alpha=0.7, **kwargs)` | `list[Polygon]` | Add a violin plot (uses Seaborn) |
| `plot_correlation(data, method="pearson", cmap="coolwarm", annot=True, fmt=".2f", **kwargs)` | `AxesImage` | Add a correlation heatmap |
| `create_dashboard(datasets, layout=(2,2), title="Dashboard", **kwargs)` | `Figure` | Create a multi-panel dashboard from `Dataset` objects |
| `finalize_plot(title=None, xlabel=None, ylabel=None, legend=None, grid=None, save_path=None)` | `Figure` | Apply labels/legend/grid, optionally save and show |
| `save_plot(path, format=None, dpi=None, bbox_inches=None, transparent=None)` | `bool` | Save the current figure to a file |
| `clear_figures()` | `None` | Close and clear all tracked figures from memory |

## Helper Functions

### `get_available_styles() -> list[str]`

Returns list of available chart style values (e.g., `["default", "minimal", "dark", ...]`).

### `get_available_palettes() -> list[str]`

Returns list of available color palette values (e.g., `["default", "viridis", "plasma", ...]`).

### `get_available_plot_types() -> list[str]`

Returns list of available plot type values (e.g., `["line", "scatter", "bar", ...]`).

## Data Structures

### Enums

#### `PlotType(Enum)`
Available plot types: `LINE`, `SCATTER`, `BAR`, `HISTOGRAM`, `PIE`, `HEATMAP`, `BOX`, `VIOLIN`, `DENSITY`, `CORRELATION`, `TIMESERIES`, `DASHBOARD`, `INTERACTIVE`.

#### `ChartStyle(Enum)`
Chart styling options: `DEFAULT`, `MINIMAL`, `DARK`, `WHITE`, `TICKS`, `DARKGRID`, `WHITEGRID`.

#### `ColorPalette(Enum)`
Color palette options: `DEFAULT`, `VIRIDIS`, `PLASMA`, `INFERNO`, `MAGMA`, `COOLWARM`, `RAINBOW`, `PASTEL`, `DARK`, `BRIGHT`.

### Dataclasses

#### `PlotConfig`
```python
@dataclass
class PlotConfig:
    title: str = ""
    xlabel: str = ""
    ylabel: str = ""
    figsize: tuple[int, int] = (10, 6)
    dpi: int = 100
    style: ChartStyle = ChartStyle.DEFAULT
    palette: ColorPalette = ColorPalette.DEFAULT
    grid: bool = True
    legend: bool = True
    tight_layout: bool = True
    save_format: str = "png"
    save_dpi: int = 300
    show_plot: bool = True
    transparent: bool = False
    bbox_inches: str = "tight"
```

#### `DataPoint`
```python
@dataclass
class DataPoint:
    x: float | int | str | datetime
    y: float | int | str | datetime
    label: str | None = None
    color: str | None = None
    size: float | None = None
    alpha: float = 1.0
```

#### `Dataset`
```python
@dataclass
class Dataset:
    name: str
    data: list[DataPoint]
    plot_type: PlotType
    color: str | None = None
    label: str | None = None
    alpha: float = 1.0
    linewidth: float = 2.0
    markersize: float = 6.0
```

## Git Visualization Functions

The module now includes specialized functions for visualizing Git repositories and operations. These functions integrate with the `git_operations` module when available.

### Function: `visualize_git_repository()`

- **Description**: Creates a comprehensive Git repository analysis with multiple visualization outputs.
- **Path**: `from codomyrmex.data_visualization import visualize_git_repository`
- **Parameters/Arguments**:
  - `repository_path` (str): Path to the Git repository to analyze.
  - `output_dir` (str, optional): Directory to save all output files. Default: `"./git_analysis"`.
  - `report_name` (str, optional): Base name for output files. Default: repository name.
- **Returns/Response**: Dictionary with status information and file paths for created visualizations.

### Function: `create_git_tree_png()`

- **Description**: Creates a PNG visualization of Git branch tree structure.
- **Path**: `from codomyrmex.data_visualization import create_git_tree_png`
- **Parameters/Arguments**:
  - `repository_path` (str, optional): Path to Git repository. If None, uses sample data.
  - `branches` (list of dict, optional): Branch information dictionaries.
  - `commits` (list of dict, optional): Commit information dictionaries.
  - `output_path` (str, optional): File path to save PNG. Default: `"git_tree.png"`.
  - `title` (str, optional): Plot title. Default: `"Git Tree Visualization"`.
- **Returns/Response**: Boolean indicating success.

### Function: `create_git_tree_mermaid()`

- **Description**: Creates a Mermaid diagram of Git branch tree structure.
- **Path**: `from codomyrmex.data_visualization import create_git_tree_mermaid`
- **Parameters/Arguments**:
  - `repository_path` (str, optional): Path to Git repository. If None, uses sample data.
  - `branches` (list of dict, optional): Branch information dictionaries.
  - `commits` (list of dict, optional): Commit information dictionaries.
  - `output_path` (str, optional): File path to save Mermaid file. Default: `"git_tree.mmd"`.
  - `title` (str, optional): Diagram title. Default: `"Git Tree Diagram"`.
- **Returns/Response**: String containing Mermaid diagram content.

## Mermaid Diagram Functions

The module includes comprehensive Mermaid diagram generation capabilities for various Git-related visualizations.

### Function: `create_git_branch_diagram()`

- **Description**: Creates a Mermaid gitgraph diagram showing branch structure and commits.
- **Path**: `from codomyrmex.data_visualization import create_git_branch_diagram`
- **Parameters/Arguments**:
  - `branches` (list of dict, optional): Branch information with names and creation dates.
  - `commits` (list of dict, optional): Commit information with hashes, messages, and dates.
  - `title` (str, optional): Diagram title. Default: `"Git Branch Diagram"`.
  - `output_path` (str, optional): File path to save Mermaid file. Default: None.
- **Returns/Response**: String containing Mermaid gitgraph content.

### Function: `create_git_workflow_diagram()`

- **Description**: Creates a Mermaid flowchart diagram showing Git workflow steps.
- **Path**: `from codomyrmex.data_visualization import create_git_workflow_diagram`
- **Parameters/Arguments**:
  - `workflow_steps` (list of dict, optional): Workflow step information with names, types, and descriptions.
  - `title` (str, optional): Diagram title. Default: `"Git Workflow"`.
  - `output_path` (str, optional): File path to save Mermaid file. Default: None.
- **Returns/Response**: String containing Mermaid flowchart content.

### Function: `create_repository_structure_diagram()`

- **Description**: Creates a Mermaid graph diagram showing repository directory structure.
- **Path**: `from codomyrmex.data_visualization import create_repository_structure_diagram`
- **Parameters/Arguments**:
  - `repo_structure` (dict, optional): Dictionary representing directory structure.
  - `title` (str, optional): Diagram title. Default: `"Repository Structure"`.
  - `output_path` (str, optional): File path to save Mermaid file. Default: None.
- **Returns/Response**: String containing Mermaid graph content.

### Function: `create_commit_timeline_diagram()`

- **Description**: Creates a Mermaid timeline diagram showing commit history over time.
- **Path**: `from codomyrmex.data_visualization import create_commit_timeline_diagram`
- **Parameters/Arguments**:
  - `commits` (list of dict, optional): Commit information with dates and messages.
  - `title` (str, optional): Diagram title. Default: `"Commit Timeline"`.
  - `output_path` (str, optional): File path to save Mermaid file. Default: None.
- **Returns/Response**: String containing Mermaid timeline content.

## Logging

All plotting functions use the `logging_monitoring` module for logging. Ensure `setup_logging()` is called before using these functions.

## Environment Setup

Use the `environment_setup` module to check/install dependencies and set up environment variables as needed.

## Versioning

This module adheres to the Codomyrmex project's overall semantic versioning strategy.

- Major version changes (X.y.z) will indicate backward-incompatible API changes to existing plotting functions.
- Minor version changes (x.Y.z) will include new plotting functions/features or significant enhancements to existing ones that are backward-compatible.
- Patch version changes (x.y.Z) will cover bug fixes, documentation updates, or minor backward-compatible tweaks to plot appearance or behavior.

All significant changes, new features, and breaking changes will be documented in the module's `CHANGELOG.md`.

## Navigation Links

- **Parent**: [Project Overview](../README.md)
- **Module Index**: [All Agents](../../AGENTS.md)
- **Documentation**: [Reference Guides](../../../docs/README.md)
- **Home**: [Root README](../../../README.md)
