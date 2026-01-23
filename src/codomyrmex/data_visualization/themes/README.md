# Themes Submodule

Color themes and styling for data visualizations.

## Overview

Provides consistent theming across all chart types with pre-defined and customizable color schemes.

## Available Themes

- `default` - Standard professional theme
- `dark` - Dark mode with vibrant accents
- `light` - Light theme with subdued colors

## Usage

```python
from codomyrmex.data_visualization.themes import apply_theme, get_color_palette

theme = apply_theme("dark")
palette = get_color_palette("dark")
```

## Custom Themes

Themes follow the structure:

```python
{
    "background": "#color",
    "foreground": "#color",
    "primary": "#color",
    "secondary": "#color",
    "accent": "#color",
    "palette": ["#c1", "#c2", ...]
}
```
