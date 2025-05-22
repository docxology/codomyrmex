# Data Visualization - Tutorial: Generating a Bar Chart

This tutorial will guide you through generating both vertical and horizontal bar charts using the Data Visualization module's direct Python functions. We'll cover plotting categorical data, basic customizations, and saving the output.

## 1. Prerequisites

Before you begin, ensure you have the following:

- The Data Visualization module installed and its dependencies (`matplotlib`, `seaborn`, `numpy`) available in your Python environment. (See main [README.md](../../README.md) and `data_visualization/requirements.txt`).
- Your Codomyrmex project environment set up, with logging initialized (see `logging_monitoring` and `environment_setup` modules).
- Basic familiarity with Python syntax and data structures (lists or NumPy arrays for values, lists of strings for categories).

## 2. Goal

By the end of this tutorial, you will be able to:

- Generate a vertical bar chart from categories and values using `create_bar_chart`.
- Generate a horizontal bar chart.
- Customize the plot with a title, axis labels, and bar color.
- Save the generated chart to an image file.

## 3. Steps

### Step 1: Prepare Your Environment and Output Directory

First, ensure your Python script initializes logging and creates an output directory for the plots.

```python
import os
import numpy as np # NumPy is useful for numerical data
from codomyrmex.logging_monitoring import setup_logging, get_logger

# Initialize logging
setup_logging()
logger = get_logger(__name__)

# Define and create an output directory
output_plot_dir = "./my_bar_charts"
os.makedirs(output_plot_dir, exist_ok=True)
logger.info(f"Bar charts will be saved to: {os.path.abspath(output_plot_dir)}")
```

### Step 2: Import the Plotting Function

Import the `create_bar_chart` function from the `data_visualization` module.

```python
from codomyrmex.data_visualization import create_bar_chart
```

### Step 3: Generate a Vertical Bar Chart

Let's plot some sample data representing monthly sales figures.

```python
# Sample data for a vertical bar chart
months = ["January", "February", "March", "April", "May"]
sales_figures = np.array([1200, 1500, 1350, 1600, 1450])

file_path_vertical_bar = os.path.join(output_plot_dir, "vertical_bar_sales.png")

create_bar_chart(
    categories=months,
    values=sales_figures,
    title="Monthly Sales Figures",
    x_label="Month",
    y_label="Sales (USD)",
    output_path=file_path_vertical_bar,
    bar_color="skyblue"
)
logger.info(f"Vertical bar chart saved to {file_path_vertical_bar}")
```

**Expected Outcome**: An image file `vertical_bar_sales.png` is saved in your `./my_bar_charts` directory.

### Step 4: Generate a Horizontal Bar Chart

Now, let's plot fictional programming language popularity horizontally.

```python
programming_languages = ['Python', 'JavaScript', 'Java', 'C#', 'TypeScript']
popularity = np.array([31.5, 20.2, 18.5, 15.1, 10.3]) # Fictional popularity scores

file_path_horizontal_bar = os.path.join(output_plot_dir, "horizontal_bar_languages.png")

create_bar_chart(
    categories=programming_languages,
    values=popularity,
    title="Programming Language Popularity (Fictional)",
    x_label="Popularity Score", # For horizontal, x_label is the value axis
    y_label="Language",         # For horizontal, y_label is the category axis
    horizontal=True,
    bar_color="lightgreen",
    output_path=file_path_horizontal_bar
)
logger.info(f"Horizontal bar chart saved to {file_path_horizontal_bar}")
```

**Expected Outcome**: An image file `horizontal_bar_languages.png` is saved in your `./my_bar_charts` directory.

### Step 5: Verify the Output

- Navigate to your `./my_bar_charts` directory.
- You should find `vertical_bar_sales.png` and `horizontal_bar_languages.png`.
- Open the images to view your bar charts.

## 4. Understanding Key Parameters

- `categories`: A list of strings for the labels of each bar.
- `values`: A list or NumPy array of numerical values corresponding to each category.
- `title`, `x_label`, `y_label`: Strings to label your chart and axes. Note how `x_label` and `y_label` are interpreted differently for horizontal charts.
- `output_path`: The file path (including name and extension) where the chart will be saved.
- `horizontal`: Boolean, if `True`, generates a horizontal bar chart. Default is `False` (vertical).
- `bar_color`: Color of the bars.

Refer to `data_visualization/API_SPECIFICATION.md` for a full list of parameters for `create_bar_chart`.

## 5. Troubleshooting

- **`ModuleNotFoundError`**: Ensure `matplotlib`, `seaborn`, `numpy` are installed.
- **`FileNotFoundError` or `PermissionError`**: Check `output_path` directory existence and permissions.
- **Data Mismatch Errors**: Ensure `categories` and `values` lists/arrays have the same number of elements.

## 6. Next Steps

- Experiment with different `bar_color` options or providing a list of colors for `bar_color`.
- Plot different categorical datasets.
- Explore other plotting functions like `create_pie_chart` for proportional data or `create_histogram` for distributions. 