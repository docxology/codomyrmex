# Data Visualization - API Specification

## Introduction

This document specifies the Application Programming Interface (API) for the Data Visualization module. The primary purpose of this API is to provide a set of Python functions for generating various types of common plots and visualizations programmatically, primarily using Matplotlib and Seaborn as backend engines.

The API is designed to be straightforward, allowing users to quickly generate visualizations with sensible defaults, while also offering customization options for titles, labels, colors, output paths, and more.

## Prerequisites & Initialization

- Ensure the `logging_monitoring` module is available and `setup_logging()` has been called at the application startup (or before using any visualization functions) for consistent logging of visualization activities.
- Dependencies such as `matplotlib`, `seaborn`, and `numpy` must be installed. Refer to `data_visualization/requirements.txt` for specific versions. It's recommended to use the `environment_setup` module or project-level scripts to verify/install dependencies.
- Python 3.7+ (or as specified by the project's root `requirements.txt`).

## General Conventions

- **Data Inputs**: Data for plotting (e.g., `x_data`, `y_data`, `values`, `data`) is typically expected as Python lists or NumPy arrays. Specific functions will detail their exact requirements.
- **Output**: Functions can either save the plot to a file (via `output_path`) and/or display it interactively (via `show_plot`). By default, plots are usually not saved or shown unless specified.
- **Return Values**: Most plotting functions do not return a value (return `None`). Their primary effect is the generation and display/saving of a plot.
- **Logging**: All public API functions integrate with the `logging_monitoring` module to log key actions, parameters, and any errors encountered.
- **Customization**: Common customizations like titles, axis labels, and colors are available as direct parameters. More advanced Matplotlib/Seaborn customizations can often be applied by obtaining the Matplotlib figure and axes objects if future versions of these functions return them (currently, they do not).

## Plotting Functions

All plotting functions are Python functions importable from `codomyrmex.data_visualization`. For example: `from codomyrmex.data_visualization import create_line_plot`.

### Function 1: `create_line_plot()`

- **Description**: Generates a line plot. Can plot single or multiple lines on the same axes.
- **Method**: N/A (Library function)
- **Path**: N/A (Importable function: `from codomyrmex.data_visualization import create_line_plot`)
- **Parameters/Arguments**:
    - `x_data` (list or np.ndarray): A list or 1D NumPy array of numerical values for the x-axis.
    - `y_data` (list, list of lists, or np.ndarray): A list of numerical values for a single y-axis, a list of lists for multiple y-axes (each inner list is a line), or a 2D NumPy array where each column (or row, depending on convention to be established) represents a line. The length of `x_data` must match the length of each y-data series.
    - `title` (str, optional): The title of the plot. Default: `"Line Plot"`.
    - `x_label` (str, optional): Label for the x-axis. Default: `"X-axis"`.
    - `y_label` (str, optional): Label for the y-axis. Default: `"Y-axis"`.
    - `output_path` (str, optional): File path to save the plot (e.g., `"./output/line_plot.png"`). If `None`, the plot is not saved. Default: `None`.
    - `show_plot` (bool, optional): If `True`, displays the plot using `plt.show()` (or equivalent). Default: `False`.
    - `line_labels` (list of str, optional): A list of strings for labeling multiple lines in the legend. Length should match the number of lines in `y_data`. Ignored for single line plots or if `y_data` is a single list/1D array. Default: Auto-generated labels (e.g., "Line 1", "Line 2").
    - `markers` (bool, optional): If True, adds markers to the data points on the line(s). Default: `False`.
- **Returns/Response**: None. Generates and potentially saves/shows a plot as a side effect.

### Function 2: `create_scatter_plot()`

- **Description**: Generates a scatter plot.
- **Method**: N/A (Library function)
- **Path**: N/A (Importable function: `from codomyrmex.data_visualization import create_scatter_plot`)
- **Parameters/Arguments**:
    - `x_data` (list or np.ndarray): A list or 1D NumPy array of numerical values for the x-axis.
    - `y_data` (list or np.ndarray): A list or 1D NumPy array of numerical values for the y-axis. Must be the same length as `x_data`.
    - `title` (str, optional): The title of the plot. Default: `"Scatter Plot"`.
    - `x_label` (str, optional): Label for the x-axis. Default: `"X-axis"`.
    - `y_label` (str, optional): Label for the y-axis. Default: `"Y-axis"`.
    - `output_path` (str, optional): File path to save the plot (e.g., `"./output/scatter_plot.png"`). If `None`, the plot is not saved. Default: `None`.
    - `show_plot` (bool, optional): If `True`, displays the plot. Default: `False`.
    - `dot_size` (int or float, optional): Size of the dots. Default: `20`.
    - `dot_color` (str, optional): Color of the dots (e.g., `'blue'`, `'#FF5733'`). Default: `'blue'`.
    - `alpha` (float, optional): Transparency of the dots (0.0 for fully transparent to 1.0 for fully opaque). Default: `0.7`.
- **Returns/Response**: None.

### Function 3: `create_bar_chart()`

- **Description**: Generates a bar chart, either vertical or horizontal.
- **Method**: N/A (Library function)
- **Path**: N/A (Importable function: `from codomyrmex.data_visualization import create_bar_chart`)
- **Parameters/Arguments**:
    - `categories` (list of str): A list of strings representing the category names for each bar.
    - `values` (list or np.ndarray): A list or 1D NumPy array of numerical values corresponding to each category. Must be the same length as `categories`.
    - `title` (str, optional): The title of the chart. Default: `"Bar Chart"`.
    - `x_label` (str, optional): Label for the x-axis (categories if vertical, values if horizontal). Default: `"Categories"`.
    - `y_label` (str, optional): Label for the y-axis (values if vertical, categories if horizontal). Default: `"Values"`.
    - `output_path` (str, optional): File path to save the chart (e.g., `"./output/bar_chart.png"`). If `None`, the chart is not saved. Default: `None`.
    - `show_plot` (bool, optional): If `True`, displays the chart. Default: `False`.
    - `horizontal` (bool, optional): If `True`, creates a horizontal bar chart. If `False` (default), creates a vertical bar chart. Default: `False`.
    - `bar_color` (str or list of str, optional): Color of the bars. Can be a single color string or a list of color strings (one per bar). Default: `'skyblue'`.
- **Returns/Response**: None.

### Function 4: `create_histogram()`

- **Description**: Generates a histogram to display the distribution of a dataset.
- **Method**: N/A (Library function)
- **Path**: N/A (Importable function: `from codomyrmex.data_visualization import create_histogram`)
- **Parameters/Arguments**:
    - `data` (list or np.ndarray): A list or 1D NumPy array of numerical values from which to generate the histogram.
    - `bins` (int or str or sequence, optional): Number of histogram bins. Can be an integer, a string (e.g., `'auto'`, `'fd'`), or a sequence specifying bin edges. Default: `10`.
    - `title` (str, optional): The title of the histogram. Default: `"Histogram"`.
    - `x_label` (str, optional): Label for the x-axis (representing the data values). Default: `"Value"`.
    - `y_label` (str, optional): Label for the y-axis (representing frequency or density). Default: `"Frequency"`.
    - `output_path` (str, optional): File path to save the histogram (e.g., `"./output/histogram.png"`). If `None`, the histogram is not saved. Default: `None`.
    - `show_plot` (bool, optional): If `True`, displays the histogram. Default: `False`.
    - `hist_color` (str, optional): Color of the histogram bars. Default: `'cornflowerblue'`.
    - `edge_color` (str, optional): Color of the edges of the histogram bars. Default: `'black'`.
    - `density` (bool, optional): If `True`, the histogram will represent a probability density. Default: `False`.
- **Returns/Response**: None.

### Function 5: `create_pie_chart()`

- **Description**: Generates a pie chart to show proportions.
- **Method**: N/A (Library function)
- **Path**: N/A (Importable function: `from codomyrmex.data_visualization import create_pie_chart`)
- **Parameters/Arguments**:
    - `labels` (list of str): A list of strings for the labels of each slice of the pie.
    - `sizes` (list or np.ndarray): A list or 1D NumPy array of numerical values representing the size (or proportion) of each slice. Values should be positive.
    - `title` (str, optional): The title of the pie chart. Default: `"Pie Chart"`.
    - `output_path` (str, optional): File path to save the chart (e.g., `"./output/pie_chart.png"`). If `None`, the chart is not saved. Default: `None`.
    - `show_plot` (bool, optional): If `True`, displays the chart. Default: `False`.
    - `autopct` (str or function, optional): A string or function used to label the wedges with their numeric value (e.g., `'%1.1f%%'` to show percentage with one decimal). Default: `'%1.1f%%'`.
    - `startangle` (float, optional): Rotates the start of the pie chart by `startangle` degrees counterclockwise from the x-axis. Default: `90`.
    - `explode` (list of float, optional): A list of floats (one for each slice) specifying the fraction of the radius with which to offset each wedge. For example, `[0, 0.1, 0]` would explode the second slice. Default: `None` (no explosion).
    - `colors` (list of str, optional): A list of color strings to use for each slice. If `None`, Matplotlib's default color cycle is used. Default: `None`.
- **Returns/Response**: None.

### Function 6: `create_heatmap()`

- **Description**: Generates a heatmap from a 2D data array, useful for visualizing matrices or correlations.
- **Method**: N/A (Library function)
- **Path**: N/A (Importable function: `from codomyrmex.data_visualization import create_heatmap`)
- **Parameters/Arguments**:
    - `data` (2D list or 2D np.ndarray): The 2D array-like data to visualize as a heatmap. Rows and columns will correspond to y-axis and x-axis ticks respectively.
    - `x_labels` (list of str, optional): Labels for the x-axis ticks (columns). Length should match the number of columns in `data`. Default: None (uses numerical indices).
    - `y_labels` (list of str, optional): Labels for the y-axis ticks (rows). Length should match the number of rows in `data`. Default: None (uses numerical indices).
    - `title` (str, optional): Title of the heatmap. Default: `"Heatmap"`.
    - `x_label` (str, optional): Overall label for the x-axis. Default: `None`.
    - `y_label` (str, optional): Overall label for the y-axis. Default: `None`.
    - `cmap` (str, optional): Matplotlib colormap name (e.g., `"viridis"`, `"YlGnBu"`, `"coolwarm"`). Default: `"viridis"`.
    - `colorbar_label` (str, optional): Label for the colorbar. Default: `None`.
    - `output_path` (str, optional): File path to save the plot (e.g., `"./output/heatmap.png"`). If `None`, the plot is not saved. Default: `None`.
    - `show_plot` (bool, optional): If `True`, displays the plot. Default: `False`.
    - `annot` (bool or 2D array-like, optional): If `True`, annotates each cell with its numerical value from `data`. If a 2D array-like of the same shape as `data` is provided, it will be used for annotations instead of `data`. Default: `False`.
    - `fmt` (str, optional): Python string formatting code to use when `annot` is `True` (e.g., `".2f"` for float with 2 decimal places, `"d"` for integer). Default: `".2f"`.
    - `linewidths` (float, optional): Width of the lines that will divide each cell. Default: `0`.
    - `linecolor` (str, optional): Color of the lines that will divide each cell. Default: `'white'`.
- **Returns/Response**: None. Generates and potentially saves/shows a plot as a side effect.

## Utility Functions (Conceptual)

The module may also contain utility functions, for example in `plot_utils.py` (not directly part of the public plotting API but used internally or available for advanced users):

- **`setup_plot_aesthetics(config: dict)` (Conceptual)**:
    - Description: Applies global aesthetic settings (e.g., font sizes, styles, default colors) if a theming or styling mechanism is implemented.
    - Parameters: `config` (dict): A dictionary of aesthetic settings.
    - Returns: None.

- **`save_plot(figure: matplotlib.figure.Figure, output_path: str, dpi: int = 300)` (Conceptual)**:
    - Description: Handles the saving of a Matplotlib figure object to a file with logging.
    - Parameters:
        - `figure` (matplotlib.figure.Figure): The figure object to save.
        - `output_path` (str): The path where the figure should be saved.
        - `dpi` (int, optional): Dots per inch for the saved image. Default: `300`.
    - Returns: `bool`: `True` if saving was successful, `False` otherwise.

- **`display_plot(figure: matplotlib.figure.Figure)` (Conceptual)**:
    - Description: Handles showing a Matplotlib figure, potentially with logic to manage multiple figures or backend considerations.
    - Parameters: `figure` (matplotlib.figure.Figure): The figure object to display.
    - Returns: None.

*Note: The utility functions listed above are conceptual and may not be directly exposed as part of the primary API. The core plotting functions (`create_line_plot`, etc.) will internally use necessary utilities for saving, showing, and logging.*

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