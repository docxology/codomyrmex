# 📊 Data Visualization Module

> **"Transform your data into stunning, publication-ready visualizations with just a few lines of code"**

The Data Visualization module provides a comprehensive suite of plotting and charting capabilities that make it easy to create beautiful, informative visualizations from your data. Built on top of Matplotlib and Seaborn, it offers both simple and advanced plotting functions with extensive customization options.

## ✨ **What You Can Create**

### **📈 Essential Chart Types**
- **Line Plots**: Trend analysis, time series data, mathematical functions
- **Bar Charts**: Comparisons, categorical data, rankings
- **Scatter Plots**: Correlations, relationships, clustering
- **Histograms**: Distributions, frequency analysis, data exploration
- **Pie Charts**: Proportions, compositions, percentages
- **Heatmaps**: Correlation matrices, 2D data patterns, intensity maps

### **🎨 Advanced Visualizations**
- **Interactive Dashboards**: Multi-chart layouts with rich formatting
- **Statistical Plots**: Box plots, violin plots, distribution comparisons
- **Geographic Maps**: Location-based data visualization
- **Network Graphs**: Relationship mapping and flow diagrams
- **3D Plots**: Surface plots, volumetric data, scientific visualization

### **📋 Customization Options**
- **13+ Chart Types** with specialized configurations
- **7 Color Palettes** including scientific, accessible, and branded options
- **Multiple Output Formats**: PNG, PDF, SVG, HTML (interactive)
- **Professional Styling**: Publication-ready figures with proper formatting
- **Responsive Design**: Charts that work in reports, presentations, and web

## 🚀 **Quick Examples**

### **📈 Line Plot - Perfect for Trends**
```python
from codomyrmex.data_visualization import create_line_plot
import numpy as np

# Create sample data
x = np.linspace(0, 10, 100)
y = np.sin(x) * np.exp(-x/5)  # Damped sine wave

# Create a beautiful line plot
create_line_plot(
    x_data=x,
    y_data=y,
    title="Damped Sine Wave",
    x_label="Time (seconds)",
    y_label="Amplitude",
    output_path="damped_wave.png",
    color="darkblue",
    linewidth=2,
    show_grid=True
)
# Result: Professional line plot saved as damped_wave.png
```

### **📊 Bar Chart - Great for Comparisons**
```python
from codomyrmex.data_visualization import create_bar_chart

# Programming language popularity data
languages = ["Python", "JavaScript", "Java", "C++", "Go", "Rust"]
popularity = [85, 72, 65, 58, 45, 38]

# Create an attractive bar chart
create_bar_chart(
    categories=languages,
    values=popularity,
    title="Programming Language Popularity (2024)",
    x_label="Programming Language",
    y_label="Popularity Score",
    output_path="language_popularity.png",
    color_palette="viridis",  # Professional color scheme
    show_values=True          # Display values on bars
)
# Result: Publication-ready bar chart with values labeled
```

### **🔥 Heatmap - Ideal for Correlations**
```python
from codomyrmex.data_visualization import create_heatmap
import numpy as np

# Create sample correlation data
data = np.random.rand(8, 8)
# Make it symmetric for correlation matrix
data = (data + data.T) / 2
np.fill_diagonal(data, 1.0)

# Variable names for axes
variables = ["Feature A", "Feature B", "Feature C", "Feature D",
             "Feature E", "Feature F", "Feature G", "Feature H"]

# Create a correlation heatmap
create_heatmap(
    data=data,
    x_labels=variables,
    y_labels=variables,
    title="Feature Correlation Matrix",
    colorbar_label="Correlation Coefficient",
    output_path="correlation_matrix.png",
    cmap="coolwarm",  # Red-blue colormap
    annot=True,       # Show correlation values
    fmt=".2f"         # Format to 2 decimal places
)
# Result: Professional correlation matrix visualization
```

### **📊 Interactive Dashboard - Multiple Charts**
```python
from codomyrmex.data_visualization import create_advanced_dashboard
from codomyrmex.data_visualization import Dataset, DataPoint, PlotType

# Prepare datasets for dashboard
datasets = [
    Dataset(
        name="Sales Trends",
        data=[DataPoint(x=i, y=i*1.2 + np.random.normal(0, 2))
              for i in range(12)],
        plot_type=PlotType.LINE,
        color="blue"
    ),
    Dataset(
        name="Market Share",
        data=[DataPoint(x=cat, y=val) for cat, val in
              [("Product A", 35), ("Product B", 28), ("Product C", 22), ("Product D", 15)]],
        plot_type=PlotType.BAR,
        color="green"
    )
]

# Create interactive dashboard
dashboard = create_advanced_dashboard(
    datasets=datasets,
    layout=(2, 1),  # 2 rows, 1 column
    title="Business Analytics Dashboard",
    output_path="business_dashboard.html",
    show_interactive=True
)
# Result: Interactive HTML dashboard with multiple charts
```

## 🛠️ **Supported Chart Types & Features**

| Chart Type | Description | Best For | Key Features |
|------------|-------------|----------|--------------|
| **📈 Line Plot** | Connect data points with lines | Trends, time series, functions | Multiple lines, markers, smooth curves |
| **📊 Bar Chart** | Vertical/horizontal bars | Comparisons, rankings, categories | Grouped bars, stacked bars, value labels |
| **🔵 Scatter Plot** | Points on 2D plane | Correlations, relationships, clusters | Bubble sizes, colors by category |
| **📊 Histogram** | Distribution of values | Frequency analysis, distributions | Multiple bins, density curves, cumulative |
| **🥧 Pie Chart** | Proportional segments | Compositions, percentages | Exploded sections, legends, custom colors |
| **🔥 Heatmap** | 2D data with colors | Matrices, correlations, patterns | Custom colormaps, annotations, clustering |
| **📊 Box Plot** | Statistical summary | Distributions, outliers, comparisons | Multiple groups, violin plots, swarm plots |
| **🌍 Geographic** | Maps with data | Location-based analysis | Country maps, city markers, choropleth |
| **🔗 Network** | Node-link diagrams | Relationships, flows, hierarchies | Force-directed layouts, path highlighting |
| **🎛️ Dashboard** | Multi-chart layouts | Comprehensive reports | Interactive HTML, multiple panels |

### **🎨 Styling & Customization**

| Feature | Options | Description |
|---------|---------|-------------|
| **Color Palettes** | Viridis, Plasma, Inferno, Magma, Cividis, Set1, Tab10 | Scientifically-designed color schemes |
| **Chart Styles** | Minimal, Classic, Modern, Scientific, Business | Pre-configured aesthetic themes |
| **Output Formats** | PNG, PDF, SVG, HTML, EPS | Publication-ready and web-compatible |
| **Figure Sizes** | Custom dimensions, DPI settings | High-resolution for any use case |
| **Typography** | Font families, sizes, weights | Professional text styling |

## 📋 **Prerequisites & Installation**
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

### **🔒 Security Considerations**
- **Safe File Handling**: All file operations include path validation and sanitization
- **Resource Limits**: Built-in safeguards prevent excessive memory usage
- **Input Validation**: All data inputs are validated before processing
- **Safe Defaults**: Secure default configurations prevent common vulnerabilities

### **💰 Cost & Performance**
- **Free to Use**: No external API costs for basic visualization
- **Fast Processing**: Typical chart generation: 0.1-2 seconds
- **Memory Efficient**: Handles datasets up to 100K points without issues
- **Storage Efficient**: Optimized file formats minimize output size

## Further Information

- [API Specification](./API_SPECIFICATION.md)
- [Usage Examples](./USAGE_EXAMPLES.md)
- [Changelog](./CHANGELOG.md)
- [Security Policy](./SECURITY.md)

---

**📝 Documentation Status**: ✅ **Verified & Signed** | *Last reviewed: January 2025* | *Maintained by: Codomyrmex Documentation Team* | *Version: v0.1.0* 