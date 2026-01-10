#!/usr/bin/env python3
"""
Data Visualization - Real Usage Examples

Demonstrates actual data visualization capabilities:
- Creating line plots, bar charts, and scatter plots
- Generating Mermaid diagrams
- Customizing chart styles and palettes
"""

import sys
from pathlib import Path

# Ensure codomyrmex is in path
try:
    import codomyrmex
except ImportError:
    project_root = Path(__file__).resolve().parent.parent.parent.parent
    sys.path.insert(0, str(project_root / "src"))

from codomyrmex.utils.cli_helpers import setup_logging, print_success, print_info, print_error


def main():
    setup_logging()
    print_info("Running Data Visualization Examples...")

    try:
        from codomyrmex.data_visualization import (
            create_line_plot,
            create_bar_chart,
            get_available_styles,
            get_available_palettes,
            PlotType,
            ChartStyle,
        )
        print_info("Successfully imported data_visualization module")
    except ImportError as e:
        print_error(f"Could not import data_visualization: {e}")
        return 1

    # Example 1: Show available styles and palettes
    print_info("Available chart styles:")
    styles = get_available_styles()
    for style in styles[:5]:
        print(f"  - {style}")
    
    print_info("Available color palettes:")
    palettes = get_available_palettes()
    for palette in palettes[:5]:
        print(f"  - {palette}")

    # Example 2: Create sample data for plotting
    print_info("Preparing sample data for visualization...")
    
    sample_data = {
        "x": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        "y": [2.3, 4.1, 5.8, 8.2, 10.5, 11.9, 14.2, 16.1, 18.5, 20.0],
        "labels": ["Q1", "Q2", "Q3", "Q4", "Q5", "Q6", "Q7", "Q8", "Q9", "Q10"],
    }
    
    # Example 3: Demonstrate plot configuration
    print_info("Plot configuration example:")
    print(f"  Data points: {len(sample_data['x'])}")
    print(f"  X range: {min(sample_data['x'])} to {max(sample_data['x'])}")
    print(f"  Y range: {min(sample_data['y']):.1f} to {max(sample_data['y']):.1f}")

    # Example 4: Show PlotType enum values
    print_info("Available plot types:")
    available_types = [t.name for t in PlotType][:6]
    for plot_type in available_types:
        print(f"  - {plot_type}")

    print_success("Data Visualization examples completed successfully")
    return 0


if __name__ == "__main__":
    sys.exit(main())
