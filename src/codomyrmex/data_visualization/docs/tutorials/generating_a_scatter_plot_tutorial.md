# Data Visualization - Tutorial: Generating a Scatter Plot

This tutorial will guide you through generating a scatter plot using the Data Visualization module's direct Python functions. We'll cover plotting data points, basic customizations, and saving the output.

## 1. Prerequisites

Before you begin, ensure you have the following:

- The Data Visualization module installed and its dependencies (`matplotlib`, `seaborn`, `numpy`) available in your Python environment. (See main [README.md](../../README.md) and `data_visualization/requirements.txt`).
- Your Codomyrmex project environment set up, with logging initialized (see `logging_monitoring` and `environment_setup` modules).
- Basic familiarity with Python syntax and data structures (lists or NumPy arrays).

## 2. Goal

By the end of this tutorial, you will be able to:

- Generate a scatter plot from X and Y data using `create_scatter_plot`.
- Customize the plot with a title, axis labels, dot size, and color.
- Save the generated plot to an image file.

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
output_plot_dir = "./my_scatter_plots"
os.makedirs(output_plot_dir, exist_ok=True)
logger.info(f"Scatter plots will be saved to: {os.path.abspath(output_plot_dir)}")
```

### Step 2: Import the Plotting Function

Import the `create_scatter_plot` function from the `data_visualization` module.

```python
from codomyrmex.data_visualization import create_scatter_plot
```

### Step 3: Generate a Scatter Plot

Let's plot some sample data representing study hours versus exam scores.

```python
# Sample data for a scatter plot
study_hours = np.array([2.5, 5.1, 3.2, 8.5, 6.5, 9.5, 2.2, 7.8, 5.4, 6.0])
exam_scores = np.array([65, 80, 62, 88, 82, 90, 60, 85, 75, 78])

file_path_scatter = os.path.join(output_plot_dir, "scatter_study_scores.png")

create_scatter_plot(
    x_data=study_hours,
    y_data=exam_scores,
    title="Study Hours vs. Exam Scores",
    x_label="Hours Studied",
    y_label="Exam Score (%)",
    output_path=file_path_scatter,
    dot_size=30,
    dot_color='coral',
    alpha=0.8 # Slightly transparent dots
)
logger.info(f"Scatter plot saved to {file_path_scatter}")
```

**Expected Outcome**: An image file `scatter_study_scores.png` is saved in your `./my_scatter_plots` directory.

### Step 4: Verify the Output

- Navigate to your `./my_scatter_plots` directory.
- You should find `scatter_study_scores.png`.
- Open the image to view your scatter plot, showing the relationship between study hours and exam scores.

## 4. Understanding Key Parameters

- `x_data`: A list or NumPy array of numerical values for the horizontal axis.
- `y_data`: A list or NumPy array of numerical values for the vertical axis. Must be the same length as `x_data`.
- `title`, `x_label`, `y_label`: Strings to label your plot and axes.
- `output_path`: The file path (including name and extension, e.g., `.png`) where the plot will be saved.
- `dot_size`: Size of the plotted points (dots).
- `dot_color`: Color of the dots.
- `alpha`: Transparency of the dots (0.0 to 1.0).

Refer to `data_visualization/API_SPECIFICATION.md` for a full list of parameters for `create_scatter_plot`.

## 5. Troubleshooting

- **`ModuleNotFoundError`**: Ensure `matplotlib`, `seaborn`, `numpy` are installed in your active Python environment.
- **`FileNotFoundError` or `PermissionError` when saving**: 
    - Check that the directory specified in `output_path` (e.g., `./my_scatter_plots/`) exists and is writable.
    - Ensure the filename in `output_path` is valid.
- **Data Mismatch Errors** (e.g., `ValueError: x and y must be the same size`):
    - Ensure `x_data` and `y_data` have the same number of elements.

## 6. Next Steps

- Experiment with other parameters of `create_scatter_plot` like different `dot_color` values or `alpha` levels.
- Try plotting different datasets to explore relationships.
- Explore other plotting functions from the `data_visualization` module, such as `create_bar_chart` or `create_histogram`.
- Consider using this function for visualizing correlations or distributions in your Codomyrmex projects. 
## Navigation Links

- **Parent**: [Project Overview](../README.md)
- **Module Index**: [All Agents](../../AGENTS.md)
- **Documentation**: [Reference Guides](../../docs/README.md)
- **Home**: [Root README](../../../README.md)
