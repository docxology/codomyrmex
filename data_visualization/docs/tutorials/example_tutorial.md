# Data Visualization - Example Tutorial: Generating a Scatter Plot

This tutorial will guide you through the process of generating a scatter plot using the Data Visualization module, specifically its `plot_scatter` (or equivalent) tool/function.

## 1. Prerequisites

Before you begin, ensure you have the following:

- The Data Visualization module installed and its dependencies (like `matplotlib`, `seaborn`, `pandas`) available in your Python environment (see main [README.md](../README.md) and `requirements.txt`).
- <!-- TODO: Specify if a particular data format is assumed (e.g., CSV file, Python lists, pandas DataFrame). For this example, let's assume Python lists. -->
- Familiarity with basic Python syntax and data structures (lists).

## 2. Goal

By the end of this tutorial, you will be able to:

- Generate a simple scatter plot from two lists of numerical data.
- Understand how to provide basic customization like title and axis labels.
- Save the generated plot to an image file.

## 3. Steps

### Step 1: Prepare Your Input Data (Python Example)

In your Python script or interactive session, define the data you want to plot. For a scatter plot, you typically need two lists of numbers of the same length, representing X and Y coordinates.

```python
# Sample data for our scatter plot
x_values = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
y_values = [2, 4, 5, 7, 6, 8, 9, 10, 12, 13]
```

### Step 2: Invoke the Scatter Plot Function

<!-- TODO: Adapt the function call and parameters below to match the actual MCP tool specification or function signature defined in `plotter.py` or the module's API. -->
Assuming the module provides an MCP tool named `create_visualization` or a direct function like `plot_scatter`:

**Using the MCP Tool (Conceptual Example - adapt to actual tool name and parameters):**

```python
# This is a conceptual representation. 
# The actual call will depend on how MCP tools are invoked in your system.

# from codomyrmex.model_context_protocol import execute_tool # or similar

plot_parameters = {
    "tool_name": "create_visualization", # or the specific plot tool name
    "parameters": {
        "plot_type": "scatter",
        "data": {
            "x": x_values,
            "y": y_values
        },
        "title": "My First Scatter Plot",
        "xlabel": "X-axis Label",
        "ylabel": "Y-axis Label",
        "output_path": "./scatter_plot.png"
    }
}

# result = execute_tool(plot_parameters)
# print(result)
```

**Using a direct Python function (Example if `plotter.py` has such a function):**

```python
# from data_visualization.plotter import plot_scatter # Assuming such a function exists

# plot_scatter(
#     x_data=x_values, 
#     y_data=y_values, 
#     title="My First Scatter Plot", 
#     xlabel="X-axis Label", 
#     ylabel="Y-axis Label", 
#     output_path="./scatter_plot.png"
# )

print(f"Scatter plot should be saved to ./scatter_plot.png")
```
<!-- TODO: Add a note here if the `plotter.py` script is primarily designed to be called as a command-line tool, and provide that example instead/as well. -->

### Step 3: Verify the Output

- Check your current working directory (or the specified `output_path`).
- You should find an image file named `scatter_plot.png` (or the name you specified).
- Open the image file. It should display a scatter plot with your data points, title, and axis labels.

## 4. Understanding the Results

The generated `scatter_plot.png` visually represents the relationship between your `x_values` and `y_values`. Each point on the plot corresponds to an (X, Y) pair from your input data.

## 5. Troubleshooting

- **Error: `ModuleNotFoundError: No module named 'matplotlib'` (or similar for `seaborn`, `pandas`)**
  - **Cause**: Required plotting libraries are not installed in your Python environment.
  - **Solution**: Install them, e.g., `pip install matplotlib seaborn pandas`. Refer to the module's `requirements.txt`.
- **Error: `Data length mismatch` (or similar)**
  - **Cause**: The lists for X and Y values have different numbers of elements.
  - **Solution**: Ensure `x_values` and `y_values` have the same length.
- **Plot is not generated or looks incorrect**:
  - Double-check the function call parameters against the module's API or MCP tool specification.
  - Ensure the input data is correctly formatted.
  - <!-- TODO: Add reference to `MCP_TOOL_SPECIFICATION.md` or `API_SPECIFICATION.md` -->
  - Consult the `MCP_TOOL_SPECIFICATION.md` for detailed parameter descriptions.

## 6. Next Steps

Congratulations on generating your first scatter plot!

Now you can try:
- Exploring other plot types offered by the module (line, bar, histogram, heatmap).
- Customizing your scatter plot further (e.g., changing colors, marker styles, adding a legend) by exploring the available parameters in the `MCP_TOOL_SPECIFICATION.md`.
- Using the visualization module with your own datasets.
- <!-- TODO: Link to other relevant tutorials or advanced guides if they exist or are planned. --> 