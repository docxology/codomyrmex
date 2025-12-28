# Codomyrmex Agents — src/codomyrmex/data_visualization

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: December 2025

## Purpose

Core module providing data visualization capabilities for the Codomyrmex platform. This module enables the creation of various chart types, plots, and visual representations using Matplotlib and Seaborn backends, supporting both programmatic generation and interactive display.

## Module Overview

### Key Capabilities
- **Chart Generation**: Create bar charts, line plots, scatter plots, histograms, and pie charts
- **Multi-Series Plotting**: Complex visualizations with multiple data series and custom styling
- **Git Visualization**: Specialized charts for version control data analysis
- **Mermaid Diagrams**: Text-based diagram generation for documentation
- **Flexible Output**: Support for file saving and interactive display
- **Customization**: Styling options for colors, labels, and formatting

### Key Features
- Matplotlib and Seaborn integration with unified interface
- Multiple chart types with consistent API patterns
- Git repository visualization and analysis
- Mermaid diagram generation for documentation
- Configurable output formats and destinations
- Integration with logging system for visualization tracking

## Function Signatures

### Basic Plotting Functions

```python
def create_line_plot(
    x_data: list,
    y_data: list,
    title: str = "Line Plot",
    x_label: str = None,
    y_label: str = None,
    color: str = "blue",
    linestyle: str = "-",
    marker: str = None,
    output_path: str = None,
    show_plot: bool = False,
    figure_size: tuple = DEFAULT_FIGURE_SIZE,
) -> str
```

Create a basic line plot.

**Parameters:**
- `x_data` (list): X-axis data points
- `y_data` (list): Y-axis data points
- `title` (str): Plot title. Defaults to "Line Plot"
- `x_label` (str): X-axis label
- `y_label` (str): Y-axis label
- `color` (str): Line color. Defaults to "blue"
- `linestyle` (str): Line style. Defaults to "-"
- `marker` (str): Data point markers. Defaults to None
- `output_path` (str): Path to save plot. If None, plot is not saved
- `show_plot` (bool): Whether to display plot interactively. Defaults to False
- `figure_size` (tuple): Figure dimensions. Defaults to DEFAULT_FIGURE_SIZE

**Returns:** `str` - Path to saved plot file if output_path provided, empty string otherwise

```python
def create_scatter_plot(
    x_data: list,
    y_data: list,
    title: str = "Scatter Plot",
    x_label: str = None,
    y_label: str = None,
    color: str = "blue",
    marker: str = "o",
    alpha: float = 0.7,
    output_path: str = None,
    show_plot: bool = False,
    figure_size: tuple = DEFAULT_FIGURE_SIZE,
) -> str
```

Create a scatter plot.

**Parameters:**
- `x_data` (list): X-axis data points
- `y_data` (list): Y-axis data points
- `title` (str): Plot title. Defaults to "Scatter Plot"
- `x_label` (str): X-axis label
- `y_label` (str): Y-axis label
- `color` (str): Point color. Defaults to "blue"
- `marker` (str): Point marker style. Defaults to "o"
- `alpha` (float): Point transparency. Defaults to 0.7
- `output_path` (str): Path to save plot. If None, plot is not saved
- `show_plot` (bool): Whether to display plot interactively. Defaults to False
- `figure_size` (tuple): Figure dimensions. Defaults to DEFAULT_FIGURE_SIZE

**Returns:** `str` - Path to saved plot file if output_path provided, empty string otherwise

```python
def create_bar_chart(
    categories: list,
    values: list,
    title: str = "Bar Chart",
    x_label: str = None,
    y_label: str = None,
    color: str = "skyblue",
    edge_color: str = "black",
    output_path: str = None,
    show_plot: bool = False,
    figure_size: tuple = DEFAULT_FIGURE_SIZE,
) -> str
```

Create a bar chart.

**Parameters:**
- `categories` (list): Category labels for bars
- `values` (list): Values for each bar
- `title` (str): Chart title. Defaults to "Bar Chart"
- `x_label` (str): X-axis label
- `y_label` (str): Y-axis label
- `color` (str): Bar fill color. Defaults to "skyblue"
- `edge_color` (str): Bar edge color. Defaults to "black"
- `output_path` (str): Path to save chart. If None, chart is not saved
- `show_plot` (bool): Whether to display chart interactively. Defaults to False
- `figure_size` (tuple): Figure dimensions. Defaults to DEFAULT_FIGURE_SIZE

**Returns:** `str` - Path to saved chart file if output_path provided, empty string otherwise

```python
def create_histogram(
    data: list,
    bins: int = 10,
    title: str = "Histogram",
    x_label: str = None,
    y_label: str = "Frequency",
    color: str = "skyblue",
    edge_color: str = "black",
    alpha: float = 0.7,
    output_path: str = None,
    show_plot: bool = False,
    figure_size: tuple = DEFAULT_FIGURE_SIZE,
) -> str
```

Create a histogram.

**Parameters:**
- `data` (list): Data values to histogram
- `bins` (int): Number of bins. Defaults to 10
- `title` (str): Histogram title. Defaults to "Histogram"
- `x_label` (str): X-axis label
- `y_label` (str): Y-axis label. Defaults to "Frequency"
- `color` (str): Bar fill color. Defaults to "skyblue"
- `edge_color` (str): Bar edge color. Defaults to "black"
- `alpha` (float): Bar transparency. Defaults to 0.7
- `output_path` (str): Path to save histogram. If None, histogram is not saved
- `show_plot` (bool): Whether to display histogram interactively. Defaults to False
- `figure_size` (tuple): Figure dimensions. Defaults to DEFAULT_FIGURE_SIZE

**Returns:** `str` - Path to saved histogram file if output_path provided, empty string otherwise

```python
def create_pie_chart(
    labels: list,
    sizes: list,
    title: str = "Pie Chart",
    colors: list = None,
    autopct: str = "%1.1f%%",
    startangle: float = 90,
    output_path: str = None,
    show_plot: bool = False,
    figure_size: tuple = DEFAULT_FIGURE_SIZE,
) -> str
```

Create a pie chart.

**Parameters:**
- `labels` (list): Labels for pie slices
- `sizes` (list): Values determining slice sizes
- `title` (str): Chart title. Defaults to "Pie Chart"
- `colors` (list): Colors for slices. If None, uses default color cycle
- `autopct` (str): Label format for percentages. Defaults to "%1.1f%%"
- `startangle` (float): Starting angle in degrees. Defaults to 90
- `output_path` (str): Path to save chart. If None, chart is not saved
- `show_plot` (bool): Whether to display chart interactively. Defaults to False
- `figure_size` (tuple): Figure dimensions. Defaults to DEFAULT_FIGURE_SIZE

**Returns:** `str` - Path to saved chart file if output_path provided, empty string otherwise

```python
def create_heatmap(
    data: list,
    x_labels: list = None,
    y_labels: list = None,
    title: str = "Heatmap",
    x_label: str = None,
    y_label: str = None,
    cmap: str = "viridis",
    colorbar_label: str = None,
    output_path: str = None,
    show_plot: bool = False,
    annot: bool = False,
    fmt: str = ".2f",
    figure_size: tuple = DEFAULT_FIGURE_SIZE,
) -> str
```

Create a heatmap visualization.

**Parameters:**
- `data` (list): 2D data array for heatmap
- `x_labels` (list): Labels for x-axis. If None, uses numeric indices
- `y_labels` (list): Labels for y-axis. If None, uses numeric indices
- `title` (str): Heatmap title. Defaults to "Heatmap"
- `x_label` (str): X-axis label
- `y_label` (str): Y-axis label
- `cmap` (str): Colormap name. Defaults to "viridis"
- `colorbar_label` (str): Label for colorbar
- `output_path` (str): Path to save heatmap. If None, heatmap is not saved
- `show_plot` (bool): Whether to display heatmap interactively. Defaults to False
- `annot` (bool): Whether to annotate cells with values. Defaults to False
- `fmt` (str): String format for annotations. Defaults to ".2f"
- `figure_size` (tuple): Figure dimensions. Defaults to DEFAULT_FIGURE_SIZE

**Returns:** `str` - Path to saved heatmap file if output_path provided, empty string otherwise

### Advanced Plotting Functions

```python
def create_advanced_line_plot(
    x_data: list[Union[float, int, str, datetime]],
    y_data: list[Union[float, int, str, datetime]],
    title: str = "",
    xlabel: str = "",
    ylabel: str = "",
    config: PlotConfig = None,
    **kwargs,
) -> plt.Figure
```

Create an advanced line plot with customizable styling and configuration.

**Parameters:**
- `x_data` (list): X-axis data (numeric, string, or datetime)
- `y_data` (list): Y-axis data (numeric, string, or datetime)
- `title` (str): Plot title. Defaults to ""
- `xlabel` (str): X-axis label. Defaults to ""
- `ylabel` (str): Y-axis label. Defaults to ""
- `config` (PlotConfig): Plot configuration object. If None, uses defaults
- `**kwargs`: Additional arguments passed to plotting functions

**Returns:** `plt.Figure` - Matplotlib figure object

```python
def create_advanced_dashboard(
    plots: list[dict],
    layout: tuple = (2, 2),
    title: str = "",
    config: PlotConfig = None,
    **kwargs,
) -> plt.Figure
```

Create a multi-panel dashboard with multiple plots.

**Parameters:**
- `plots` (list[dict]): List of plot specifications
- `layout` (tuple): Dashboard layout (rows, cols). Defaults to (2, 2)
- `title` (str): Dashboard title. Defaults to ""
- `config` (PlotConfig): Plot configuration object
- `**kwargs`: Additional customization arguments

**Returns:** `plt.Figure` - Matplotlib figure object

### Configuration Functions

```python
def get_available_styles() -> list[ChartStyle]
```

Get list of available chart styles.

**Returns:** `list[ChartStyle]` - Available chart style options

```python
def get_available_palettes() -> list[ColorPalette]
```

Get list of available color palettes.

**Returns:** `list[ColorPalette]` - Available color palette options

```python
def get_available_plot_types() -> list[PlotType]
```

Get list of available plot types.

**Returns:** `list[PlotType]` - Available plot type options

### Git Visualization Functions

```python
def visualize_git_repository(
    repo_path: str,
    output_path: str = None,
    visualization_type: str = "branch_structure",
    **kwargs,
) -> str
```

Create visualizations of Git repository data.

**Parameters:**
- `repo_path` (str): Path to Git repository
- `output_path` (str): Path to save visualization. If None, uses default path
- `visualization_type` (str): Type of visualization. Defaults to "branch_structure"
- `**kwargs`: Additional visualization options

**Returns:** `str` - Path to generated visualization file

### Mermaid Diagram Functions

```python
def create_git_branch_diagram(repo_path: str, **kwargs) -> str
```

Create Mermaid diagram showing Git branch structure.

**Parameters:**
- `repo_path` (str): Path to Git repository
- `**kwargs`: Additional diagram options

**Returns:** `str` - Mermaid diagram text

```python
def create_git_workflow_diagram(repo_path: str, **kwargs) -> str
```

Create Mermaid diagram showing Git workflow.

**Parameters:**
- `repo_path` (str): Path to Git repository
- `**kwargs`: Additional diagram options

**Returns:** `str` - Mermaid diagram text

```python
def create_repository_structure_diagram(repo_path: str, **kwargs) -> str
```

Create Mermaid diagram of repository file structure.

**Parameters:**
- `repo_path` (str): Path to Git repository
- `**kwargs`: Additional diagram options

**Returns:** `str` - Mermaid diagram text

```python
def create_commit_timeline_diagram(repo_path: str, **kwargs) -> str
```

Create Mermaid diagram showing commit timeline.

**Parameters:**
- `repo_path` (str): Path to Git repository
- `**kwargs`: Additional diagram options

**Returns:** `str` - Mermaid diagram text

## Active Components

### Core Implementation
- `__init__.py` – Module initialization and public API exports
- `plotter.py` – Main plotting interface and utilities
- `advanced_plotter.py` – Complex multi-series plotting capabilities
- `plot_utils.py` – Shared plotting utilities and helpers

### Chart Types
- `line_plot.py` – Line chart generation
- `bar_chart.py` – Bar chart creation
- `scatter_plot.py` – Scatter plot visualization
- `histogram.py` – Histogram and distribution plotting
- `pie_chart.py` – Pie chart generation

### Specialized Visualizations
- `git_visualizer.py` – Git repository analysis and visualization
- `mermaid_generator.py` – Text-based diagram generation

### Documentation
- `README.md` – Module usage and overview
- `API_SPECIFICATION.md` – Complete API documentation
- `USAGE_EXAMPLES.md` – Practical usage demonstrations
- `MCP_TOOL_SPECIFICATION.md` – AI agent tool specifications
- `SECURITY.md` – Security considerations for data visualization
- `CHANGELOG.md` – Version history and updates

### Supporting Files
- `requirements.txt` – Module dependencies (matplotlib, seaborn, numpy)
- `docs/` – Additional documentation
- `tests/` – Comprehensive test suite

## Operating Contracts

### Universal Visualization Protocols

All data visualization within the Codomyrmex platform must:

1. **Consistent Styling** - Use unified color schemes and formatting across charts
2. **Accessible Output** - Support both file saving and interactive display modes
3. **Data Validation** - Validate input data before plotting attempts
4. **Error Handling** - Gracefully handle plotting failures with informative messages
5. **Performance Aware** - Optimize for large datasets and complex visualizations

### Module-Specific Guidelines

#### Chart Generation
- Provide sensible defaults for all chart parameters
- Support customization through explicit parameters
- Include axis labels, titles, and legends by default
- Handle different data types (lists, numpy arrays, pandas dataframes)

#### Output Management
- Default to file saving over interactive display for automation
- Support multiple image formats (PNG, SVG, PDF)
- Provide configurable output paths and naming
- Log visualization operations for monitoring

#### Data Handling
- Accept multiple data formats (Python lists, NumPy arrays)
- Validate data dimensions and types before plotting
- Handle missing or invalid data points gracefully
- Support both single and multi-series visualizations

## Navigation Links

### Module Documentation
- **Module Overview**: [README.md](README.md) - Complete module documentation
- **API Reference**: [API_SPECIFICATION.md](API_SPECIFICATION.md) - Detailed API specification
- **Usage Examples**: [USAGE_EXAMPLES.md](USAGE_EXAMPLES.md) - Practical usage demonstrations

### Related Modules

### Platform Navigation
- **Parent Directory**: [codomyrmex](../README.md) - Package overview
- **Project Root**: [README](../../../README.md) - Main project documentation

## Agent Coordination

### Integration Points

When integrating with other modules:

1. **Data Sources** - Coordinate with modules providing data for visualization
2. **Output Integration** - Support embedding visualizations in reports and documentation
3. **Configuration Sharing** - Use consistent styling across platform visualizations
4. **Performance Monitoring** - Track visualization generation performance

### Quality Gates

Before visualization changes are accepted:

1. **Chart Accuracy Verified** - Generated charts correctly represent input data
2. **Output Formats Tested** - All supported formats (PNG, SVG, PDF) working
3. **Data Validation Complete** - Robust handling of edge cases and invalid data
4. **Performance Optimized** - Efficient processing of large datasets
5. **Styling Consistent** - Visualizations follow platform design standards

## Version History

- **v0.1.0** (December 2025) - Initial comprehensive visualization system with multiple chart types and output formats
