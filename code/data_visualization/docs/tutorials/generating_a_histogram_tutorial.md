# Data Visualization - Tutorial: Generating a Histogram

This tutorial will guide you through generating a histogram to visualize the distribution of a dataset, using the Data Visualization module's direct Python functions. We'll cover basic customizations and saving the output.

## 1. Prerequisites

Before you begin, ensure you have the following:

- The Data Visualization module installed and its dependencies (`matplotlib`, `seaborn`, `numpy`) available in your Python environment. (See main [README.md](../../README.md) and `data_visualization/requirements.txt`).
- Your Codomyrmex project environment set up, with logging initialized (see `logging_monitoring` and `environment_setup` modules).
- Basic familiarity with Python syntax and data structures (lists or NumPy arrays).

## 2. Goal

By the end of this tutorial, you will be able to:

- Generate a histogram from a numerical dataset using `create_histogram`.
- Customize the plot with a title, axis labels, number of bins, and colors.
- Understand the option to plot a probability density.
- Save the generated histogram to an image file.

## 3. Steps

### Step 1: Prepare Your Environment and Output Directory

First, ensure your Python script initializes logging and creates an output directory for the plots.

```python
import os
import numpy as np # NumPy is essential for numerical data and often used with histograms
import random # For generating sample data
from codomyrmex.logging_monitoring import setup_logging, get_logger

# Initialize logging
setup_logging()
logger = get_logger(__name__)

# Define and create an output directory
output_plot_dir = "./my_histograms"
os.makedirs(output_plot_dir, exist_ok=True)
logger.info(f"Histograms will be saved to: {os.path.abspath(output_plot_dir)}")
```

### Step 2: Import the Plotting Function

Import the `create_histogram` function from the `data_visualization` module.

```python
from codomyrmex.data_visualization import create_histogram
```

### Step 3: Generate a Histogram

Let's plot a histogram of simulated exam scores.

```python
# Simulate exam scores for 200 students
np.random.seed(42) # for reproducibility
exam_scores = np.random.normal(loc=75, scale=10, size=200) # Mean 75, StdDev 10
exam_scores = np.clip(exam_scores, 0, 100) # Ensure scores are between 0 and 100

file_path_histogram = os.path.join(output_plot_dir, "histogram_exam_scores.png")

create_histogram(
    data=exam_scores,
    bins=15, # Number of bins
    title="Distribution of Student Exam Scores",
    x_label="Exam Score (%)",
    y_label="Number of Students (Frequency)",
    output_path=file_path_histogram,
    hist_color="mediumseagreen",
    edge_color="black"
)
logger.info(f"Histogram saved to {file_path_histogram}")

# Example of a density histogram
file_path_density_hist = os.path.join(output_plot_dir, "histogram_scores_density.png")
create_histogram(
    data=exam_scores,
    bins="auto", # Let Matplotlib decide the optimal number of bins
    title="Density Plot of Student Exam Scores",
    x_label="Exam Score (%)",
    y_label="Density",
    output_path=file_path_density_hist,
    hist_color="skyblue",
    edge_color="darkblue",
    density=True
)
logger.info(f"Density histogram saved to {file_path_density_hist}")
```

**Expected Outcome**: Two image files, `histogram_exam_scores.png` (frequency histogram) and `histogram_scores_density.png` (density histogram), are saved in your `./my_histograms` directory.

### Step 4: Verify the Output

- Navigate to your `./my_histograms` directory.
- You should find the two PNG files.
- Open the images to view your histograms, showing the distribution of exam scores.

## 4. Understanding Key Parameters

- `data`: A list or 1D NumPy array of numerical values to be binned.
- `bins`: Defines the number of equal-width bins in the range. Can be an integer, a sequence of bin edges, or a string like 'auto'.
- `title`, `x_label`, `y_label`: Strings to label your plot and axes.
- `output_path`: The file path where the histogram will be saved.
- `hist_color`: Fill color of the histogram bars.
- `edge_color`: Color of the edges of the bars.
- `density`: Boolean. If `True`, the result is the value of the probability density function at the bin, normalized such that the integral over the range is 1.

Refer to `data_visualization/API_SPECIFICATION.md` for a full list of parameters for `create_histogram`.

## 5. Troubleshooting

- **`ModuleNotFoundError`**: Ensure `matplotlib`, `seaborn`, `numpy` are installed.
- **`FileNotFoundError` or `PermissionError`**: Check `output_path` directory existence and permissions.
- **Invalid `data`**: Ensure `data` is a list or 1D array of numerical values.

## 6. Next Steps

- Experiment with different numbers of `bins` or binning strategies (e.g., providing a sequence of bin edges).
- Plot distributions of different datasets from your projects.
- Explore using the `density=True` option to compare the shape of distributions regardless of sample size.
- Try other visualization functions like `create_box_plot` (if available) or `create_violin_plot` (if available) for alternative ways to see distributions. 