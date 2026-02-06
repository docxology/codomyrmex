# Personal AI Infrastructure — Dark Module

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

The Dark module provides PAI integration for dark mode and theming support.

## PAI Capabilities

### Theme Management

Manage themes:

```python
from codomyrmex.dark import ThemeManager

themes = ThemeManager()
themes.set_theme("dark")

current = themes.current_theme()
print(f"Current: {current}")
```

### Color Schemes

Access color schemes:

```python
from codomyrmex.dark import ColorScheme

scheme = ColorScheme("monokai")
bg = scheme.get("background")
fg = scheme.get("foreground")
```

## PAI Integration Points

| Component | PAI Use Case |
|-----------|-------------|
| `ThemeManager` | Manage themes |
| `ColorScheme` | Color palettes |
| `DarkMode` | Toggle dark mode |

## Navigation

- [README](README.md) | [AGENTS](AGENTS.md) | [SPEC](SPEC.md)
