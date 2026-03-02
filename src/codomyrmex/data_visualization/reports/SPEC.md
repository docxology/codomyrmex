# Reports -- Technical Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

Domain-specific HTML report generators. Each report extends `BaseReport`, composes a `Dashboard` internally, and provides `generate()` / `save()` methods. Four report types cover finance, general system metrics, logistics with flow diagrams, and marketing analytics.

## Architecture

```
BaseReport (@dataclass)
  ├── title, sections
  ├── add_section(section)
  ├── render() -> <article> HTML
  ├── save(output_path) -> write HTML file
  └── to_dict() -> {title, section_count}
       |
       ├── FinanceReport      -- Dashboard + Card (Net Profit, Stock)
       ├── GeneralSystemReport -- Dashboard + Card (Revenue, Colony, Connections, Progress)
       ├── LogisticsReport     -- Dashboard + Card + SankeyDiagram
       └── MarketingReport     -- Dashboard + Card (Brand Awareness, Acquisition)
```

## Key Classes

### `BaseReport`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `add_section` | `section: Any` | `None` | Append a renderable section |
| `render` | -- | `str` | `<article><h1>title</h1>...sections...</article>` |
| `save` | `output_path: str` | `str` | Write HTML and return path |
| `to_dict` | -- | `dict` | `{title, section_count}` |

### `FinanceReport`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `generate` | -- | `None` | Populate dashboard with finance metrics |
| `save` | `output_path: str` | `str` | Auto-generates if needed, writes HTML |

### `GeneralSystemReport`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `generate` | -- | `None` | Populate with Revenue, Colony Size, Connections, Progress cards |
| `save` | `output_path: str` | `str` | Auto-generates if needed, writes HTML |

### `LogisticsReport`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `generate` | -- | `None` | Populate with shipment card and SankeyDiagram (Warehouse -> Distribution -> Retail) |
| `save` | `output_path: str` | `str` | Auto-generates if needed, writes HTML |

### `MarketingReport`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `generate` | -- | `None` | Populate with Brand Awareness and User Acquisition cards |
| `save` | `output_path: str` | `str` | Auto-generates if needed, writes HTML |

## Dependencies

- **Internal**: `data_visualization.core.ui` (`Card`, `Dashboard`), `data_visualization.plots.sankey` (`SankeyDiagram`)
- **External**: None (reports compose existing visualization components)

## Constraints

- `generate()` is idempotent: tracked by `_generated` flag; repeated calls are safe.
- `save()` always calls `generate()` if not yet called, ensuring reports are never empty.
- Reports produce standalone HTML files with embedded CSS from the Dashboard theme.
- Zero-mock: all content is real rendered HTML; `NotImplementedError` for unimplemented paths.

## Error Handling

- `save()` writes via `Path.write_text()`; file system errors propagate to the caller.
- No exceptions for empty data; reports render with whatever sections have been added.
