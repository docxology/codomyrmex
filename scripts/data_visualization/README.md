# Data Visualization Orchestrator

Thin orchestrator script providing CLI access to the `codomyrmex.data_visualization` module.

## Purpose

This orchestrator provides command-line interface for creating various types of plots, charts, and visualizations.

## Usage

```bash
# Create line plot
python scripts/data_visualization/orchestrate.py line-plot --output output/line.png --title "My Line Plot"

# Create scatter plot from data file
python scripts/data_visualization/orchestrate.py scatter-plot --data-file data.json --output output/scatter.png

# Create bar chart
python scripts/data_visualization/orchestrate.py bar-chart --output output/bar.png --title "Bar Chart"

# Create histogram
python scripts/data_visualization/orchestrate.py histogram --output output/hist.png --title "Distribution"

# Create pie chart
python scripts/data_visualization/orchestrate.py pie-chart --output output/pie.png --title "Pie Chart"

# Create heatmap
python scripts/data_visualization/orchestrate.py heatmap --output output/heat.png --title "Heatmap"

# Visualize git repository
python scripts/data_visualization/orchestrate.py git-visualize --repo . --output ./git_analysis
```

## Commands

- `line-plot` - Create line plot
- `scatter-plot` - Create scatter plot
- `bar-chart` - Create bar chart
- `histogram` - Create histogram
- `pie-chart` - Create pie chart
- `heatmap` - Create heatmap
- `git-visualize` - Visualize git repository structure

## Related Documentation

- **[Module README](../../src/codomyrmex/data_visualization/README.md)**: Complete module documentation
- **[API Specification](../../src/codomyrmex/data_visualization/API_SPECIFICATION.md)**: Detailed API reference
- **[Usage Examples](../../src/codomyrmex/data_visualization/USAGE_EXAMPLES.md)**: Practical examples
- **[CLI Reference](../../docs/reference/cli.md)**: Main CLI documentation

## Integration

This orchestrator calls functions from:
- `codomyrmex.data_visualization.create_line_plot`
- `codomyrmex.data_visualization.create_scatter_plot`
- `codomyrmex.data_visualization.create_bar_chart`
- `codomyrmex.data_visualization.create_histogram`
- `codomyrmex.data_visualization.create_pie_chart`
- `codomyrmex.data_visualization.create_heatmap`
- `codomyrmex.data_visualization.visualize_git_repository`

See `codomyrmex.cli.py` for main CLI integration.

