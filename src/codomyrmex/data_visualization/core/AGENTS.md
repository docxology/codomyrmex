# Codomyrmex Agents -- src/codomyrmex/data_visualization/core

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose

Core infrastructure for the data_visualization module: layout management (`Grid`, `Section`), theme configuration (`Theme`, `DEFAULT_THEME`, `DARK_THEME`), higher-level UI containers (`Card`, `Table`, `Dashboard`), and HTML export utilities (`render_html`).

## Key Components

| File | Class / Function | Role |
|------|-----------------|------|
| `layout.py` | `Section` | A titled container that renders children as HTML |
| `layout.py` | `Grid` | CSS Grid layout with configurable columns and gap |
| `theme.py` | `Theme` | Dataclass holding colour scheme, font, and border-radius settings |
| `theme.py` | `DEFAULT_THEME`, `DARK_THEME` | Pre-built theme instances |
| `ui.py` | `Card` | Card component with title, content, value, and description |
| `ui.py` | `Table` | HTML table from headers and rows lists |
| `ui.py` | `Dashboard` | Top-level container combining a `Grid`, `Theme`, and `render()` to full HTML |
| `export.py` | `render_html()` | Wraps content in a complete HTML5 document with theme CSS variables |

## Operating Contracts

- `Theme.to_css_vars()` returns a dictionary of CSS custom properties (`--primary`, `--secondary`, `--bg`, `--text`, `--font`, `--font-size`, `--radius`).
- `Dashboard.render()` produces a complete HTML page with embedded CSS from the active theme.
- `Dashboard.render(output_path=...)` writes the HTML to disk if a path is provided.
- `Grid.add_section()` computes width from column count; `full_width=True` overrides to 100%.
- `render_html()` applies `:root` CSS variables and writes to file when `output_path` is given.

## Integration Points

- **Depends on**: Python stdlib (`dataclasses`, `pathlib`)
- **Used by**: `data_visualization.reports` (all report classes compose `Dashboard` + `Card`), `data_visualization.components` (can be embedded in sections)

## Navigation

- **Parent**: [data_visualization](../README.md)
- **Root**: [Root](../../../../README.md)
