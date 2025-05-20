# Data Visualization - API Specification

## Introduction

This document specifies the Application Programming Interface (API) for the Data Visualization module. The primary purpose of this API is to provide a set of functions for generating various types of plots and visualizations programmatically using Matplotlib.

## Prerequisites & Initialization

- Ensure the `logging_monitoring` module is available and `setup_logging()` is called at application startup for consistent logging.
- Use the `environment_setup` module to check/install dependencies and set up environment variables (see project root README and environment_setup docs).
- Python 3.7+ and `matplotlib` must be installed (see requirements.txt).

## Endpoints / Functions / Interfaces

All functions are Python functions importable from `codomyrmex.data_visualization`.

### Function 1: `create_line_plot()`

- **Description**: Generates a line plot. Can plot single or multiple lines on the same axes.
- **Method**: N/A (Library function)
- **Path**: N/A (Importable function: `from codomyrmex.data_visualization import create_line_plot`)
- **Parameters/Arguments**:
    - `x_data` (list): A list of numerical values for the x-axis.
    - `y_data` (list or list of lists): A list of numerical values for the y-axis. If a list of lists, each inner list is plotted as a separate line against `x_data`.
    - `title` (str, optional): The title of the plot. Default: "Line Plot".
    - `x_label` (str, optional): Label for the x-axis. Default: "X-axis".
    - `y_label` (str, optional): Label for the y-axis. Default: "Y-axis".
    - `output_path` (str, optional): File path to save the plot (e.g., "./plot.png"). If None, plot is not saved. Default: `None`.
    - `show_plot` (bool, optional): If True, displays the plot using `plt.show()`. Default: `False`.
    - `line_labels` (list, optional): A list of strings for labeling multiple lines in the legend. Ignored for single line plots. Default: Auto-generated labels like "Line 1", "Line 2".
    - `markers` (bool, optional): If True, adds markers to the data points on the line(s). Default: `False`.
- **Returns/Response**: None. Generates and potentially saves/shows a plot as a side effect.

### Function 2: `create_scatter_plot()`

- **Description**: Generates a scatter plot.
- **Method**: N/A (Library function)
- **Path**: N/A (Importable function: `from codomyrmex.data_visualization import create_scatter_plot`)
- **Parameters/Arguments**:
    - `x_data` (list): A list of numerical values for the x-axis.
    - `y_data` (list): A list of numerical values for the y-axis.
    - `title` (str, optional): The title of the plot. Default: "Scatter Plot".
    - `x_label` (str, optional): Label for the x-axis. Default: "X-axis".
    - `y_label` (str, optional): Label for the y-axis. Default: "Y-axis".
    - `output_path` (str, optional): File path to save the plot. Default: `None`.
    - `show_plot` (bool, optional): If True, displays the plot. Default: `False`.
    - `dot_size` (int, optional): Size of the dots. Default: `20`.
    - `dot_color` (str, optional): Color of the dots. Default: `'blue'`.
    - `alpha` (float, optional): Transparency of the dots (0.0 to 1.0). Default: `0.7`.
- **Returns/Response**: None.

### Function 3: `create_bar_chart()`

- **Description**: Generates a bar chart, either vertical or horizontal.
- **Method**: N/A (Library function)
- **Path**: N/A (Importable function: `from codomyrmex.data_visualization import create_bar_chart`)
- **Parameters/Arguments**:
    - `categories` (list): A list of strings representing the categories.
    - `values` (list): A list of numerical values corresponding to each category.
    - `title` (str, optional): The title of the chart. Default: "Bar Chart".
    - `x_label` (str, optional): Label for the x-axis (categories). Default: "Categories".
    - `y_label` (str, optional): Label for the y-axis (values). Default: "Values".
    - `output_path` (str, optional): File path to save the chart. Default: `None`.
    - `show_plot` (bool, optional): If True, displays the chart. Default: `False`.
    - `horizontal` (bool, optional): If True, creates a horizontal bar chart. Default: `False` (vertical).
    - `bar_color` (str, optional): Color of the bars. Default: `'skyblue'`.
- **Returns/Response**: None.

### Function 4: `create_histogram()`

- **Description**: Generates a histogram to display the distribution of a dataset.
- **Method**: N/A (Library function)
- **Path**: N/A (Importable function: `from codomyrmex.data_visualization import create_histogram`)
- **Parameters/Arguments**:
    - `data` (list): A list of numerical values.
    - `bins` (int, optional): Number of bins in the histogram. Default: `10`.
    - `title` (str, optional): The title of the histogram. Default: "Histogram".
    - `x_label` (str, optional): Label for the x-axis (value). Default: "Value".
    - `y_label` (str, optional): Label for the y-axis (frequency). Default: "Frequency".
    - `output_path` (str, optional): File path to save the histogram. Default: `None`.
    - `show_plot` (bool, optional): If True, displays the histogram. Default: `False`.
    - `hist_color` (str, optional): Color of the histogram bars. Default: `'cornflowerblue'`.
    - `edge_color` (str, optional): Color of the edges of the bars. Default: `'black'`.
- **Returns/Response**: None.

### Function 5: `create_pie_chart()`

- **Description**: Generates a pie chart to show proportions.
- **Method**: N/A (Library function)
- **Path**: N/A (Importable function: `from codomyrmex.data_visualization import create_pie_chart`)
- **Parameters/Arguments**:
    - `labels` (list): A list of strings for the labels of each slice.
    - `sizes` (list): A list of numerical values representing the size of each slice.
    - `title` (str, optional): The title of the pie chart. Default: "Pie Chart".
    - `output_path` (str, optional): File path to save the chart. Default: `None`.
    - `show_plot` (bool, optional): If True, displays the chart. Default: `False`.
    - `autopct` (str, optional): A string or function used to label the wedges with their numeric value (e.g., `'%1.1f%%'`). Default: `'%1.1f%%'`.
    - `startangle` (int, optional): Rotates the start of the pie chart by `startangle` degrees counterclockwise from the x-axis. Default: `90`.
    - `explode` (list, optional): A list of floats (one for each slice) specifying the fraction of the radius with which to offset each wedge. Default: `None`.
- **Returns/Response**: None.

### Function 6: `create_heatmap()`

- **Description**: Generates a heatmap from a 2D data array.
- **Parameters/Arguments**:
    - `data` (list of lists or 2D np.ndarray): The data to visualize.
    - `x_labels` (list, optional): Labels for the x-axis.
    - `y_labels` (list, optional): Labels for the y-axis.
    - `title` (str, optional): Title of the heatmap. Default: "Heatmap".
    - `x_label` (str, optional): X-axis label.
    - `y_label` (str, optional): Y-axis label.
    - `cmap` (str, optional): Matplotlib colormap. Default: "viridis".
    - `colorbar_label` (str, optional): Label for the colorbar.
    - `output_path` (str, optional): File path to save the plot. Default: None.
    - `show_plot` (bool, optional): If True, displays the plot. Default: False.
    - `annot` (bool, optional): If True, annotates each cell with its value. Default: False.
    - `fmt` (str, optional): Format string for annotations. Default: ".2f".
- **Returns/Response**: None.

## Logging

All plotting functions use the `logging_monitoring` module for logging. Ensure `setup_logging()` is called before using these functions.

## Environment Setup

Use the `environment_setup` module to check/install dependencies and set up environment variables as needed.

## Versioning

<!-- TODO: Confirm the versioning strategy. Typically, this module will follow the overall project's semantic versioning. 
Changes to function signatures or significantly altered plot outputs would constitute minor or major version bumps. 
New plot types would be minor version additions. Bug fixes (e.g., correcting plot rendering issues) would be patch versions. 
All significant changes should be noted in the module's CHANGELOG.md. --> 