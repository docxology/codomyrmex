# Themes - Technical Specification

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
