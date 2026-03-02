# Core -- Technical Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

Foundation layer for data_visualization providing layout primitives, theme management, high-level UI containers, and HTML export. All classes produce self-contained HTML and can be composed into dashboards and reports.

## Architecture

```
Theme           -- colour, font, border config -> CSS variables
  |
Grid + Section  -- CSS Grid layout of renderable children
  |
Dashboard       -- combines Theme + Grid, renders full HTML page
  |
render_html()   -- standalone HTML5 document generator with theme
```

## Key Classes

### `Theme` (theme.py)

| Method / Property | Parameters | Returns | Description |
|-------------------|-----------|---------|-------------|
| `__init__` | `name, **kwargs` | -- | Accepts `primary`, `accent`/`secondary`, `background`, `text`, `font_family`, `font_size`, `border_radius` |
| `to_css_vars` | -- | `dict[str, str]` | CSS custom properties dict |
| `css` | -- | `str` | Full CSS `body { ... }` block |
| `to_dict` | -- | `dict` | Serialized theme settings |

Pre-built instances: `DEFAULT_THEME` (light), `DARK_THEME` (dark blue/green).

### `Section` (layout.py)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `title` | `str` | `""` | Section heading |
| `children` | `list[Any]` | `[]` | Renderable child objects |
| `width` | `str` | `"100%"` | CSS width |

### `Grid` (layout.py)

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `add_section` | `title, content=None, full_width=False` | `None` | Add a titled section to the grid |
| `render` | -- | `str` | CSS Grid HTML with `grid-template-columns: repeat(N, 1fr)` |

### `Dashboard` (ui.py)

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `__init__` | `title, theme=None` | -- | Creates internal Grid and applies theme |
| `add_section` | `title, content=None, **kwargs` | `None` | Delegates to `Grid.add_section` |
| `render` | `output_path=None` | `str` | Full HTML page; writes to file if path given |

### `render_html()` (export.py)

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `content` | `str` | -- | HTML body content |
| `title` | `str` | `"Codomyrmex Report"` | Page title |
| `theme` | `Theme` | `DEFAULT_THEME` | Theme for CSS variables |
| `output_path` | `str/Path` | `None` | Optional file path to write HTML |

## Dependencies

- **Internal**: None (pure Python)
- **External**: None

## Constraints

- `Grid` width calculation is simplistic: `100/columns`%. For precise control, use `Section.width` directly.
- `Dashboard.render()` produces a minimal HTML page (no JavaScript, no external resources).
- Zero-mock: all rendering produces real HTML; `NotImplementedError` for unimplemented paths.

## Error Handling

- `Dashboard.render(output_path=...)` writes via `Path.write_text()`; exceptions propagate to the caller.
- `Theme.__init__` uses `kwargs.get()` with defaults for all optional parameters.
