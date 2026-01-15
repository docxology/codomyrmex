# Data Visualization - Tutorial: Generating a Line Plot

This tutorial will guide you through generating a line plot using the Data Visualization module's direct Python functions. We'll cover plotting single and multiple lines, basic customizations, and saving the output.

## 1. Prerequisites

Before you begin, ensure you have the following:

- The Data Visualization module installed and its dependencies (`matplotlib`, `seaborn`, `numpy`) available in your Python environment. (See main [README.md](../../README.md) and `data_visualization/requirements.txt`).
- Your Codomyrmex project environment set up, with logging initialized (see `logging_monitoring` and `environment_setup` modules).
- Basic familiarity with Python syntax and data structures (lists).

## 2. Goal

By the end of this tutorial, you will be able to:

- Generate a simple line plot from X and Y data using `create_line_plot`.
- Plot multiple lines on the same axes.
- Customize the plot with a title, axis labels, and line labels.
- Save the generated plot to an image file.

## 3. Steps

### Step 1: Prepare Your Environment and Output Directory

First, ensure your Python script initializes logging and creates an output directory for the plots.

```python
import os
from codomyrmex.logging_monitoring import setup_logging, get_logger

# Initialize logging
setup_logging()
logger = get_logger(__name__)

# Define and create an output directory
output_plot_dir = "./my_plots"
os.makedirs(output_plot_dir, exist_ok=True)
logger.info(f"Plots will be saved to: {os.path.abspath(output_plot_dir)}")
```

### Step 2: Import the Plotting Function

Import the `create_line_plot` function from the `data_visualization` module.

```python
from codomyrmex.data_visualization import create_line_plot
```

### Step 3: Generate a Single Line Plot

Let's plot some sample temperature data over a week.

```python
# Sample data for a single line plot
days = [1, 2, 3, 4, 5, 6, 7]
temperatures_city_a = [15, 16, 18, 20, 19, 22, 21] # Celsius

file_path_single = os.path.join(output_plot_dir, "single_line_temperature.png")

create_line_plot(
    x_data=days,
    y_data=temperatures_city_a,
    title="Weekly Temperature Trend - City A",
    x_label="Day of Week",
    y_label="Temperature (°C)",
    output_path=file_path_single,
    markers=True # Add markers to data points
)
logger.info(f"Single line plot saved to {file_path_single}")
```

**Expected Outcome**: An image file `single_line_temperature.png` is saved in your `./my_plots` directory.

### Step 4: Generate a Plot with Multiple Lines

Now, let's compare temperatures for two cities.

```python
# Sample data for multiple lines
# days variable is the same as above
temperatures_city_b = [12, 14, 15, 17, 18, 20, 19] # Celsius

file_path_multiple = os.path.join(output_plot_dir, "multiple_lines_temperatures.png")

create_line_plot(
    x_data=days,
    y_data=[temperatures_city_a, temperatures_city_b],
    title="Weekly Temperature Comparison",
    x_label="Day of Week",
    y_label="Temperature (°C)",
    line_labels=["City A", "City B"], # Labels for the legend
    output_path=file_path_multiple,
    markers=True
)
logger.info(f"Multiple lines plot saved to {file_path_multiple}")
```

**Expected Outcome**: An image file `multiple_lines_temperatures.png` is saved, showing two lines with a legend.

### Step 5: Verify the Output

- Navigate to your `./my_plots` directory.
- You should find `single_line_temperature.png` and `multiple_lines_temperatures.png`.
- Open the images to view your plots.

## 4. Understanding Key Parameters

- `x_data`: A list of values for the horizontal axis.
- `y_data`: A list of values (for a single line) or a list of lists (for multiple lines) for the vertical axis.
- `title`, `x_label`, `y_label`: Strings to label your plot and axes.
- `output_path`: The file path (including name and extension, e.g., `.png`) where the plot will be saved.
- `line_labels`: A list of strings used to create a legend when plotting multiple lines. The order should correspond to the order of lists in `y_data`.
- `markers`: A boolean to show or hide markers at each data point.

Refer to `data_visualization/API_SPECIFICATION.md` for a full list of parameters for `create_line_plot` and other functions.

## 5. Troubleshooting

- **`ModuleNotFoundError`**: Ensure `matplotlib`, `seaborn`, `numpy` are installed in your active Python environment.
- **`FileNotFoundError` or `PermissionError` when saving**: 
    - Check that the directory specified in `output_path` (e.g., `./my_plots/`) exists and is writable.
    - Ensure the filename in `output_path` is valid.
- **Data Mismatch Errors** (e.g., `ValueError: x and y must be the same size`):
    - Ensure `x_data` and each list in `y_data` have the same number of elements.
    - If plotting multiple lines, ensure `line_labels` has the same number of items as there are lists in `y_data`.

## 6. Next Steps

- Experiment with other parameters of `create_line_plot` (see `API_SPECIFICATION.md`).
- Try other plotting functions from the `data_visualization` module like `create_scatter_plot` or `create_bar_chart`.
- Integrate these plotting functions into your own data analysis scripts within the Codomyrmex project. 
## Navigation Links

- **Parent**: [Project Overview](../README.md)
- **Module Index**: [All Agents](../../AGENTS.md)
- **Documentation**: [Reference Guides](../../README.md)
- **Home**: [Root README](../../README.md)
