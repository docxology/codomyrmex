# Data Visualization

## Overview

The Data Visualization module for Codomyrmex provides a suite of functions to generate common plot types using Matplotlib and Seaborn. It is tightly integrated with the Codomyrmex logging and environment setup systems for robust, reproducible, and well-logged visualizations.

Key features:
- Generation of line plots, scatter plots, bar charts, histograms, pie charts, and heatmaps.
- Customizable plot titles, labels, colors, and other visual aspects.
- Option to save plots to various file formats or display them directly.
- **Integrated logging**: Uses the `logging_monitoring` module for all logging (ensure `setup_logging()` is called in your main app).
- **Environment checks**: Use the `environment_setup` module to verify dependencies and environment variables.

## Prerequisites & Initialization

- Python 3.7+ (Confirm with root `requirements.txt` or `environment_setup` for project-wide Python version).
- `matplotlib`
- `seaborn`
- `numpy`
- (These are listed in `data_visualization/requirements.txt` and should be installed via `pip install -r data_visualization/requirements.txt` after setting up the project environment).
- `logging_monitoring` module (for logging).
- `environment_setup` module (for environment/dependency checks).

**Recommended initialization (typically in your main application script):**

```python
from codomyrmex.logging_monitoring import setup_logging, get_logger
from codomyrmex.environment_setup.env_checker import ensure_dependencies_installed

# Initialize logging system (as per logging_monitoring module)
setup_logging()
logger = get_logger(__name__) # Get a logger for your current module/script

# Check for required project and module dependencies
# This function might be part of environment_setup or a project-level script
# ensure_dependencies_installed(module_requirements_path="data_visualization/requirements.txt") 
# For simplicity, ensure matplotlib, seaborn, and numpy are in your environment.

logger.info("Logging and environment setup complete for Data Visualization usage.")
```

## Key Components

- **Plotting Functions**: Located in individual files (e.g., `line_plot.py`, `heatmap.py`) and exposed through `plotter.py` and the module's `__init__.py`.
    - `create_line_plot`
    - `create_scatter_plot`
    - `create_bar_chart`
    - `create_histogram`
    - `create_pie_chart`
    - `create_heatmap`
- **`plot_utils.py`**: Contains helper functions for logging, saving plots, and applying common aesthetics.
- **Matplotlib & Seaborn**: The underlying plotting libraries providing the core visualization capabilities.
- **NumPy**: Used for numerical operations, often as a prerequisite for data manipulation before plotting.
- **Logging Integration**: All plotting functions utilize the `logging_monitoring` module.
- **Environment Integration**: Relies on `environment_setup` for managing dependencies.

## Available Visualizations

This module provides functions to create a variety of standard plots:

- `create_line_plot()`: For visualizing trends over continuous data.
- `create_scatter_plot()`: For showing relationships between two numerical variables.
- `create_bar_chart()`: For comparing categorical data.
- `create_histogram()`: For understanding the distribution of a single numerical variable.
- `create_pie_chart()`: For displaying proportions of a whole.
- `create_heatmap()`: For visualizing 2D data matrices with color intensity.

Detailed parameters for each function are available in the [API Specification](./API_SPECIFICATION.md).

## Usage Example

```python
# Ensure recommended initialization (logging, env checks) has been performed.
from codomyrmex.data_visualization import create_heatmap
import numpy as np

# Example data
data = np.random.rand(5, 8)
x_labels = [f'Col {i+1}' for i in range(8)]
y_labels = [f'Row {i+1}' for i in range(5)]

# Create and save a heatmap
create_heatmap(
    data=data,
    x_labels=x_labels,
    y_labels=y_labels,
    title="Sample Heatmap",
    output_path="./output/sample_heatmap.png", # Ensure ./output directory exists
    annot=True,
    cmap="YlGnBu"
)

print("Heatmap generated and saved to ./output/sample_heatmap.png")
```

Ensure the `./output/` directory (or your specified `output_path` directory) exists before running examples that save plots.

## Development

- **Modularity**: Each plot type (line, bar, etc.) is implemented in its own Python file (e.g., `line_plot.py`). These are then imported and exposed via `plotter.py` and the main `__init__.py`.
- **Utilities**: Common functionalities like logger retrieval, plot saving, and aesthetic settings are centralized in `plot_utils.py`.
- **Logging**: Adhere to using the `logging_monitoring.get_logger(__name__)` pattern within each file for consistent logging.
- **Dependencies**: All direct Python dependencies for this module (matplotlib, seaborn, numpy) are listed in `data_visualization/requirements.txt`.

### Building & Testing

This module is Python-based and does not require a separate build step.

- **Install Dependencies**: Ensure development and module dependencies are installed:
  ```bash
  pip install -r requirements.txt  # Project root requirements
  pip install -r data_visualization/requirements.txt # Module specific
  pip install pytest # Or your project's test runner
  ```
- **Running Tests**: Execute tests using `pytest` (or the project's chosen test runner). Tests are located in the `data_visualization/tests/` directory.
  ```bash
  pytest data_visualization/tests/unit
  pytest data_visualization/tests/integration
  ```
  Refer to `data_visualization/tests/README.md` for more detailed testing instructions.
  Unit tests should verify the logic of individual plotting functions (e.g., correct Matplotlib calls are made based on inputs), possibly by mocking `plt.show()` and `fig.savefig()` or by analyzing plot objects. Integration tests might involve generating actual plot files to a temporary directory and (optionally) performing basic checks on them (e.g., file existence, non-zero size).

## Further Information

- [API Specification](./API_SPECIFICATION.md)
- [Usage Examples](./USAGE_EXAMPLES.md)
- [Changelog](./CHANGELOG.md)
- [Security Policy](./SECURITY.md) 