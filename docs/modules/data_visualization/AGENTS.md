# Data Visualization Module — Agent Coordination

## Purpose

Data Visualization Module for Codomyrmex.

## Key Capabilities

- **ChartStyle**: Fallback chart style enum.
- **ColorPalette**: Fallback color palette enum.
- **PlotType**: Fallback plot type enum.
- `get_available_styles()`: Get available chart styles.
- `get_available_palettes()`: Get available color palettes.
- `get_available_plot_types()`: Get available plot types.

## Agent Usage Patterns

```python
from codomyrmex.data_visualization import ChartStyle

# Agent initializes data visualization
instance = ChartStyle()
```

## Integration Points

- **Source**: [src/codomyrmex/data_visualization/](../../../src/codomyrmex/data_visualization/)
- **Docs**: [Module Documentation](README.md)
- **Spec**: [Technical Specification](SPEC.md)

## Testing Guidelines

```bash
uv run python -m pytest src/codomyrmex/tests/ -k data_visualization -v
```

- Run tests before and after making changes.
- Ensure all existing tests pass before submitting.
