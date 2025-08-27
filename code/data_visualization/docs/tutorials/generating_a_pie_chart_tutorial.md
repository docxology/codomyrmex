# Data Visualization - Tutorial: Generating a Pie Chart

This tutorial will guide you through generating a pie chart to visualize proportions of a whole, using the Data Visualization module's direct Python functions. We'll cover basic customizations like exploding slices, adding percentages, and saving the output.

## 1. Prerequisites

Before you begin, ensure you have the following:

- The Data Visualization module installed and its dependencies (`matplotlib`, `seaborn`, `numpy`) available in your Python environment. (See main [README.md](../../README.md) and `data_visualization/requirements.txt`).
- Your Codomyrmex project environment set up, with logging initialized (see `logging_monitoring` and `environment_setup` modules).
- Basic familiarity with Python syntax and data structures (lists or NumPy arrays for sizes, lists of strings for labels).

## 2. Goal

By the end of this tutorial, you will be able to:

- Generate a pie chart from labels and corresponding sizes using `create_pie_chart`.
- Customize the chart with a title, slice labels, percentages, and exploded slices.
- Save the generated pie chart to an image file.

## 3. Steps

### Step 1: Prepare Your Environment and Output Directory

First, ensure your Python script initializes logging and creates an output directory for the plots.

```python
import os
import numpy as np # NumPy can be used for numerical data
from codomyrmex.logging_monitoring import setup_logging, get_logger

# Initialize logging
setup_logging()
logger = get_logger(__name__)

# Define and create an output directory
output_plot_dir = "./my_pie_charts"
os.makedirs(output_plot_dir, exist_ok=True)
logger.info(f"Pie charts will be saved to: {os.path.abspath(output_plot_dir)}")
```

### Step 2: Import the Plotting Function

Import the `create_pie_chart` function from the `data_visualization` module.

```python
from codomyrmex.data_visualization import create_pie_chart
```

### Step 3: Generate a Pie Chart

Let's plot a pie chart representing a fictional budget allocation.

```python
# Sample data for a pie chart
budget_categories = ['Housing', 'Food', 'Transportation', 'Entertainment', 'Savings']
budget_allocation = np.array([30, 20, 15, 10, 25]) # Percentages or amounts

# Explode the 'Savings' slice (5th slice)
explode_slices = (0, 0, 0, 0, 0.1)

custom_colors = ['gold', 'yellowgreen', 'lightcoral', 'lightskyblue', 'lightpink']

file_path_pie = os.path.join(output_plot_dir, "pie_chart_budget.png")

create_pie_chart(
    labels=budget_categories,
    sizes=budget_allocation,
    title="Monthly Budget Allocation",
    output_path=file_path_pie,
    autopct='%1.1f%%', # Show percentages on slices
    startangle=90,      # Start the first slice at the top
    explode=explode_slices,
    colors=custom_colors
)
logger.info(f"Pie chart saved to {file_path_pie}")
```

**Expected Outcome**: An image file `pie_chart_budget.png` is saved in your `./my_pie_charts` directory, showing the budget allocation with the "Savings" slice slightly pulled out.

### Step 4: Verify the Output

- Navigate to your `./my_pie_charts` directory.
- You should find `pie_chart_budget.png`.
- Open the image to view your pie chart.

## 4. Understanding Key Parameters

- `labels`: A list of strings for the labels of each slice.
- `sizes`: A list or 1D NumPy array of numerical values representing the size of each slice. These are typically positive values.
- `title`: String to label your chart.
- `output_path`: The file path where the pie chart will be saved.
- `autopct`: A string format or function to label wedges with their numeric value (e.g., `'%1.1f%%'` for percentage).
- `startangle`: Rotates the starting point of the pie chart.
- `explode`: A tuple or list of floats, one for each slice, specifying the fraction of the radius to offset each wedge.
- `colors`: A list of color strings to use for the slices.

Refer to `data_visualization/API_SPECIFICATION.md` for a full list of parameters for `create_pie_chart`.

## 5. Troubleshooting

- **`ModuleNotFoundError`**: Ensure `matplotlib`, `seaborn`, `numpy` are installed.
- **`FileNotFoundError` or `PermissionError`**: Check `output_path` directory existence and permissions.
- **Data Mismatch Errors**: Ensure `labels` and `sizes` have the same number of elements. If using `explode` or `colors`, ensure they also match the number of slices.
- **Negative `sizes`**: Pie charts typically require non-negative values for `sizes`.

## 6. Next Steps

- Experiment with different `startangle` values and `explode` combinations.
- Try creating a pie chart without `autopct` or with a custom function for it.
- Use different color palettes or let Matplotlib choose default colors by not providing the `colors` parameter.
- Plot proportional data from your own projects, such as survey results or market share data. 