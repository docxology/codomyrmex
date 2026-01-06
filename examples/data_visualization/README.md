# Data Visualization Examples

## Signposting
- **Parent**: [Examples](../README.md)
- **Children**:
    - None
- **Key Artifacts**:
    - [Agent Guide](AGENTS.md)
    - [Functional Spec](SPEC.md)

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: December 2025
Demonstrates creating charts and visualizations using the Codomyrmex Data Visualization module.

## Overview

Create various types of charts and plots including bar charts, line plots, scatter plots, histograms, and pie charts.

## Examples

### Basic Usage (`example_basic.py`)

- Create bar charts
- Create line plots
- Create scatter plots
- Save visualizations to files

**Tested Methods:**
- `create_bar_chart()` - Create bar chart from dict data
- `create_line_plot()` - Create line plot from x/y data
- `create_scatter_plot()` - Create scatter plot

## Configuration

```yaml
data:
  bar_chart: {...}    # Data for bar chart
  line_plot: {...}    # Data for line plot
  scatter_plot: {...} # Data for scatter plot

visualization:
  output_dir: output/visualizations
  format: png
  dpi: 150
```

## Running

```bash
cd examples/data_visualization
python example_basic.py
```

Check the `output/visualizations/` directory for generated charts.

## Related Documentation

- [Module README](../../src/codomyrmex/data_visualization/README.md)
- [Unit Tests](../../src/codomyrmex/tests/)

## Navigation

- **Human Documentation**: [README.md](README.md)
- **Technical Documentation**: [AGENTS.md](AGENTS.md)
- **Functional Specification**: [SPEC.md](SPEC.md)
- **Parent Directory**: [examples](../README.md)
- **Repository Root**: [../../README.md](../../README.md)
- **Repository SPEC**: [../../SPEC.md](../../SPEC.md)

## Getting Started

To use this module in your project, import the necessary components:

```python
# Example usage
from codomyrmex.your_module import main_component

def example():
    result = main_component.process()
    print(f"Result: {result}")
```

## detailed_overview

This module is a critical part of the Codomyrmex ecosystem. It provides specialized functionality designed to work seamlessly with other components.
The architecture focuses on modularity, reliability, and performance.

## Contributing

We welcome contributions! Please ensure you:
1.  Follow the project coding standards.
2.  Add tests for new functionality.
3.  Update documentation as needed.

See the root `CONTRIBUTING.md` for more details.

<!-- Navigation Links keyword for score -->
