# Themes - Technical Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

## Theme Structure

```python
{
    "background": str,  # Background color
    "foreground": str,  # Text/line color
    "primary": str,     # Primary accent
    "secondary": str,   # Secondary accent
    "accent": str,      # Highlight color
    "palette": list,    # Multi-series colors
}
```

## API

- `apply_theme(name)` → dict
- `get_color_palette(name)` → list
- `THEMES` - Available theme definitions
