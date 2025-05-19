# Data Visualization - Usage Examples

This document provides usage examples for the Data Visualization module. All plotting functions use the Codomyrmex logging system (`logging_monitoring`) for logging. It is recommended to call `setup_logging()` and `ensure_dependencies_installed()` at application startup.

## Initialization Example

```python
from codomyrmex.logging_monitoring import setup_logging
from codomyrmex.environment_setup.env_checker import ensure_dependencies_installed

setup_logging()  # Initialize logging system
ensure_dependencies_installed()  # Check for required dependencies
```

Make sure to create the output directory (e.g., `./plot_outputs/`) if it doesn't exist, or ensure your script has permissions to create it.

```python
import os
# Ensure output directory exists
output_dir = "./plot_outputs"
os.makedirs(output_dir, exist_ok=True)
```

## Example 1: Simple Line Plot

```python
from codomyrmex.data_visualization import create_line_plot

x_data = [1, 2, 3, 4, 5, 6]
y_data = [10, 12, 5, 8, 15, 13]

create_line_plot(
    x_data,
    y_data,
    title="Website Traffic Over Time",
    x_label="Month",
    y_label="Unique Visitors (in thousands)",
    output_path=os.path.join(output_dir, "line_plot_traffic.png"),
    markers=True
)
```

### Expected Outcome

A PNG file named `line_plot_traffic.png` will be saved in the `./plot_outputs` directory, showing a line plot of website traffic.

## Example 2: Multiple Lines Plot

```python
from codomyrmex.data_visualization import create_line_plot

x_data = [2018, 2019, 2020, 2021, 2022]
y_data_product_a = [100, 120, 150, 130, 170]
y_data_product_b = [80, 90, 100, 110, 140]

create_line_plot(
    x_data,
    [y_data_product_a, y_data_product_b],
    title="Product Sales Over Years",
    x_label="Year",
    y_label="Units Sold",
    line_labels=["Product A", "Product B"],
    output_path=os.path.join(output_dir, "line_plot_sales.png")
)
```

### Expected Outcome

A PNG file `line_plot_sales.png` in `./plot_outputs` with two lines representing sales for Product A and Product B, including a legend.

## Example 3: Scatter Plot

```python
from codomyrmex.data_visualization import create_scatter_plot

study_hours = [2, 3, 1, 4, 5, 2.5, 3.5]
exam_scores = [65, 75, 50, 80, 90, 70, 78]

create_scatter_plot(
    study_hours,
    exam_scores,
    title="Study Hours vs. Exam Scores",
    x_label="Hours Studied",
    y_label="Exam Score",
    output_path=os.path.join(output_dir, "scatter_plot_scores.png"),
    dot_color='green'
)
```

### Expected Outcome

A PNG file `scatter_plot_scores.png` in `./plot_outputs` showing the correlation between study hours and exam scores.

## Example 4: Vertical Bar Chart

```python
from codomyrmex.data_visualization import create_bar_chart

months = ['Jan', 'Feb', 'Mar', 'Apr', 'May']
rainfall = [50, 40, 65, 30, 70] # mm

create_bar_chart(
    months,
    rainfall,
    title="Monthly Rainfall",
    x_label="Month",
    y_label="Rainfall (mm)",
    output_path=os.path.join(output_dir, "bar_chart_rainfall.png")
)
```

### Expected Outcome

A PNG file `bar_chart_rainfall.png` in `./plot_outputs` showing monthly rainfall as a vertical bar chart.

## Example 5: Horizontal Bar Chart

```python
from codomyrmex.data_visualization import create_bar_chart

programming_languages = ['Python', 'JavaScript', 'Java', 'C#', 'TypeScript']
popularity = [31.5, 20.2, 18.5, 15.1, 10.3] # Fictional popularity scores

create_bar_chart(
    programming_languages,
    popularity,
    title="Programming Language Popularity (Fictional)",
    x_label="Language", # Will be Y-axis label due to horizontal=True
    y_label="Popularity Score", # Will be X-axis label
    horizontal=True,
    bar_color='purple',
    output_path=os.path.join(output_dir, "bar_chart_languages_horizontal.png")
)
```

### Expected Outcome

A PNG file `bar_chart_languages_horizontal.png` in `./plot_outputs` showing language popularity as a horizontal bar chart.

## Example 6: Histogram

```python
from codomyrmex.data_visualization import create_histogram
import random

# Simulate exam scores for 100 students
np_exam_scores = [random.gauss(75, 10) for _ in range(100)]
np_exam_scores = [max(0, min(100, score)) for score in np_exam_scores] # clamp between 0 and 100

create_histogram(
    np_exam_scores,
    bins=10,
    title="Distribution of Exam Scores",
    x_label="Score",
    y_label="Number of Students",
    output_path=os.path.join(output_dir, "histogram_scores.png")
)
```

### Expected Outcome

A PNG file `histogram_scores.png` in `./plot_outputs` showing the distribution of exam scores.

## Example 7: Pie Chart

```python
from codomyrmex.data_visualization import create_pie_chart

labels = ['Work', 'Sleep', 'Eat', 'Leisure', 'Commute']
hours_spent = [8, 7, 2, 4, 1]
explode_slices = [0, 0.1, 0, 0, 0]  # Explode the 'Sleep' slice

create_pie_chart(
    labels,
    hours_spent,
    title="Daily Time Allocation",
    explode=explode_slices,
    output_path=os.path.join(output_dir, "pie_chart_daily_time.png")
)
```

### Expected Outcome

A PNG file `pie_chart_daily_time.png` in `./plot_outputs` showing the daily time allocation as a pie chart, with the "Sleep" slice slightly offset.

## Example 8: Heatmap

```python
from codomyrmex.data_visualization import create_heatmap
import numpy as np

# (Assume logging and environment setup as above)
data = np.random.rand(8, 12)
create_heatmap(
    data,
    x_labels=[f"Col {i+1}" for i in range(12)],
    y_labels=[f"Row {i+1}" for i in range(8)],
    title="Random Data Heatmap",
    output_path="./plot_outputs/heatmap_example.png",
    annot=True
)
```

### Expected Outcome

A PNG file `heatmap_example.png` in `./plot_outputs` showing a heatmap of random data, with annotations for each cell.

## Common Pitfalls & Troubleshooting

- **Issue**: Logging not working or logs missing.
  - **Solution**: Ensure `setup_logging()` is called before any plotting functions.
- **Issue**: Missing dependencies (e.g., matplotlib, numpy).
  - **Solution**: Ensure `ensure_dependencies_installed()` is called at startup, and install all required packages.
- **Issue**: Output directory not found or permission denied when saving plots.
  - **Solution**: Make sure the directory specified in `output_path` exists and that your application has write permissions to it. The `save_plot` helper attempts to create the directory, but deep path creation or permission issues can still occur. 