# data_visualization/themes

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

Theme definitions for data visualization. Provides predefined color schemes and styling configurations that can be applied to matplotlib charts and other visualization libraries. Includes six built-in themes covering default, dark, light, vibrant, minimal, and scientific presentation styles.

## Key Exports

### Enums

- **`ThemeName`** -- Available theme identifiers: `DEFAULT`, `DARK`, `LIGHT`, `VIBRANT`, `MINIMAL`, `SCIENTIFIC`

### Data Classes

- **`ColorPalette`** -- Color configuration with primary, secondary, accent, background, foreground, semantic colors (success/warning/error/info), and a series color list. Includes `get_series_color(index)` with automatic cycling
- **`FontConfig`** -- Font configuration for charts: family, title/label/tick/legend sizes, and weight
- **`GridConfig`** -- Grid configuration: show/hide toggle, color, alpha transparency, line style, and line width
- **`Theme`** -- Complete theme definition combining `ColorPalette`, `FontConfig`, `GridConfig`, figure/axes face colors, and spine styling. Includes `to_matplotlib_rcparams()` for direct matplotlib integration

### Predefined Themes

- **`THEMES`** -- Dictionary mapping `ThemeName` to `Theme` instances. Six built-in themes:
  - **DEFAULT** -- Standard 10-color Tableau-like palette on white background
  - **DARK** -- Neon-bright colors on dark navy background (#1a1a2e)
  - **LIGHT** -- Bootstrap-inspired palette on light gray background
  - **VIBRANT** -- High-saturation bold colors on white
  - **MINIMAL** -- Grayscale 4-color palette with hidden grid and subtle spines
  - **SCIENTIFIC** -- Publication-ready sequential palette with serif fonts

### Functions

- **`get_theme()`** -- Retrieve a theme by `ThemeName`, falls back to DEFAULT
- **`apply_theme()`** -- Apply a Theme directly to matplotlib via `plt.rcParams.update()`
- **`list_themes()`** -- Return list of all available theme name strings

## Directory Contents

- `__init__.py` - Theme classes, predefined theme definitions, and utility functions (216 lines)
- `py.typed` - PEP 561 typing marker
- `SPEC.md` - Module specification
- `AGENTS.md` - Agent integration documentation
- `PAI.md` - PAI integration notes

## Navigation

- **Parent Module**: [data_visualization](../README.md)
- **Project Root**: [codomyrmex](../../../../README.md)
