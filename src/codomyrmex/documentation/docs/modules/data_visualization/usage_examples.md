# Data Visualization - Usage Examples

This document provides usage examples for the Data Visualization module. All plotting functions use the Codomyrmex logging system (`logging_monitoring`) for logging. It is recommended to call `setup_logging()` and `ensure_dependencies_installed()` at application startup.

## Initialization Example

```python
from codomyrmex.logging_monitoring import setup_logging
# from codomyrmex.environment_setup.env_checker import ensure_dependencies_installed # Conceptual: ensure this function exists or use project-specific setup

setup_logging()  # Initialize logging system
# ensure_dependencies_installed()  # Conceptual: Check for required dependencies
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
import numpy as np
import os

# Ensure output directory exists
output_dir = "./plot_outputs"
os.makedirs(output_dir, exist_ok=True)

x_data = np.array([1, 2, 3, 4, 5, 6])
y_data = np.array([10, 12, 5, 8, 15, 13])

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
import numpy as np
import os

# Ensure output directory exists
output_dir = "./plot_outputs"
os.makedirs(output_dir, exist_ok=True)

x_data = np.array([2018, 2019, 2020, 2021, 2022])
y_data_product_a = np.array([100, 120, 150, 130, 170])
y_data_product_b = np.array([80, 90, 100, 110, 140])

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
import numpy as np
import os

# Ensure output directory exists
output_dir = "./plot_outputs"
os.makedirs(output_dir, exist_ok=True)

study_hours = np.array([2, 3, 1, 4, 5, 2.5, 3.5])
exam_scores = np.array([65, 75, 50, 80, 90, 70, 78])

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
import numpy as np
import os

# Ensure output directory exists
output_dir = "./plot_outputs"
os.makedirs(output_dir, exist_ok=True)

months = ['Jan', 'Feb', 'Mar', 'Apr', 'May']
rainfall = np.array([50, 40, 65, 30, 70]) # mm

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
import numpy as np
import os

# Ensure output directory exists
output_dir = "./plot_outputs"
os.makedirs(output_dir, exist_ok=True)

programming_languages = ['Python', 'JavaScript', 'Java', 'C#', 'TypeScript']
popularity = np.array([31.5, 20.2, 18.5, 15.1, 10.3]) # Fictional popularity scores

create_bar_chart(
    programming_languages,
    popularity,
    title="Programming Language Popularity (Fictional)",
    x_label="Popularity Score", # Becomes the value axis label for horizontal charts
    y_label="Language", # Becomes the category axis label for horizontal charts
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
import numpy as np
import random
import os

# Ensure output directory exists
output_dir = "./plot_outputs"
os.makedirs(output_dir, exist_ok=True)

# Simulate exam scores for 100 students
np_exam_scores_raw = [random.gauss(75, 10) for _ in range(100)]
np_exam_scores = np.clip(np_exam_scores_raw, 0, 100) # clamp between 0 and 100

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
import numpy as np
import os

# Ensure output directory exists
output_dir = "./plot_outputs"
os.makedirs(output_dir, exist_ok=True)

labels = ['Work', 'Sleep', 'Eat', 'Leisure', 'Commute']
hours_spent = np.array([8, 7, 2, 4, 1])
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
import os

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

A PNG file `heatmap_example.png` will be saved in the `./plot_outputs` directory, displaying a heatmap of random data with annotations.

## Using Plotting Tools via Model Context Protocol (MCP)

The Data Visualization module also exposes its plotting functions as MCP tools. This allows AI agents or other Codomyrmex modules to request plot generation programmatically.

Full details for each MCP tool, including all parameters, are available in the [MCP Tool Specification](./MCP_TOOL_SPECIFICATION.md).

Below are a couple of examples of how these tools might be invoked.

### MCP Example 1: Creating a Line Plot

**Request:**
```json
{
  "tool_name": "create_line_plot",
  "arguments": {
    "x_data": [1, 2, 3, 4, 5],
    "y_data": [2, 3, 5, 7, 6],
    "title": "MCP Generated Line Plot",
    "x_label": "Time (s)",
    "y_label": "Value",
    "output_path": "./plot_outputs/mcp_line_plot.png",
    "markers": true
  }
}
```

**Expected Outcome (via MCP Response and file system):**
- An MCP response similar to: `{"output_path": "./plot_outputs/mcp_line_plot.png", "fig_details": {"status": "saved_to_path"}}` (Actual path in response might be absolute if server resolves it).
- A PNG file named `mcp_line_plot.png` saved in the `./plot_outputs` directory (or other designated MCP output location).

### MCP Example 2: Creating a Bar Chart

**Request:**
```json
{
  "tool_name": "create_bar_chart",
  "arguments": {
    "categories": ["Alpha", "Bravo", "Charlie", "Delta"],
    "values": [15, 22, 18, 25],
    "title": "MCP Generated Bar Chart",
    "x_label": "Group",
    "y_label": "Count",
    "output_path": "./plot_outputs/mcp_bar_chart.png",
    "horizontal": false,
    "bar_color": "teal"
  }
}
```

**Expected Outcome (via MCP Response and file system):**
- An MCP response similar to: `{"output_path": "./plot_outputs/mcp_bar_chart.png", "fig_details": {"status": "saved_to_path"}}`.
- A PNG file named `mcp_bar_chart.png` saved in the `./plot_outputs` directory.

### MCP Example 3: Creating a Histogram

**Request:**
```json
{
  "tool_name": "create_histogram",
  "arguments": {
    "data": [10,12,12,13,14,14,15,15,15,16,18,20,21,21,22,25,30],
    "bins": 5,
    "title": "MCP Generated Histogram",
    "x_label": "Measurement",
    "y_label": "Frequency",
    "output_path": "./plot_outputs/mcp_histogram.png",
    "hist_color": "#FF9900",
    "density": false
  }
}
```

**Expected Outcome (via MCP Response and file system):**
- An MCP response similar to: `{"output_path": "./plot_outputs/mcp_histogram.png", "fig_details": {"status": "saved_to_path"}}`.
- A PNG file named `mcp_histogram.png` saved in the `./plot_outputs` directory.

### MCP Example 4: Creating a Pie Chart

**Request:**
```json
{
  "tool_name": "create_pie_chart",
  "arguments": {
    "labels": ["Alpha", "Bravo", "Charlie", "Delta"],
    "sizes": [20, 30, 25, 25],
    "title": "MCP Generated Pie Chart",
    "output_path": "./plot_outputs/mcp_pie_chart.png",
    "explode": [0, 0.1, 0, 0],
    "startangle": 90,
    "autopct": "%1.1f%%"
  }
}
```

**Expected Outcome (via MCP Response and file system):**
- An MCP response similar to: `{"output_path": "./plot_outputs/mcp_pie_chart.png", "fig_details": {"status": "saved_to_path"}}`.
- A PNG file named `mcp_pie_chart.png` saved in the `./plot_outputs` directory.

### General Notes for MCP Usage:

-   **`output_path`**: Ensure the path specified is writable by the Codomyrmex application process and ideally within a designated output area to prevent arbitrary file writes.
-   **Error Handling**: MCP tool calls will return an error structure in the JSON response if plot generation fails (e.g., due to invalid data or parameters). Check the `MCP_TOOL_SPECIFICATION.md` for details on error responses.
-   **Data Types**: Ensure data passed in the `arguments` field matches the types specified in the `MCP_TOOL_SPECIFICATION.md` (e.g., arrays of numbers for `x_data`, `y_data`).

For detailed specifications of all available MCP plotting tools, including `create_scatter_plot`, `create_histogram`, `create_pie_chart`, and `create_heatmap`, please refer to the [Data Visualization MCP Tool Specification](./MCP_TOOL_SPECIFICATION.md).

## Common Pitfalls & Troubleshooting

- **Issue**: Logging not working or logs missing.
  - **Solution**: Ensure `setup_logging()` is called before any plotting functions.
- **Issue**: Missing dependencies (e.g., matplotlib, numpy).
  - **Solution**: Ensure `ensure_dependencies_installed()` is called at startup, and install all required packages.
- **Issue**: Output directory not found or permission denied when saving plots.
  - **Solution**: Make sure the directory specified in `output_path` exists and that your application has write permissions to it. The `save_plot` helper attempts to create the directory, but deep path creation or permission issues can still occur. 