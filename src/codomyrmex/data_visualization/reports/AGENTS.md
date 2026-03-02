# Codomyrmex Agents -- src/codomyrmex/data_visualization/reports

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose

Domain-specific report generators built on `BaseReport`. Each report composes a `Dashboard` with `Card` components and optional plot embeds, providing `generate()` to populate content and `save()` to write HTML output. Four report types are included: finance, general system, logistics (with Sankey diagram), and marketing.

## Key Components

| File | Class | Role |
|------|-------|------|
| `_base.py` | `BaseReport` | Abstract base with `title`, `sections` list, `add_section()`, `render()`, `save()`, `to_dict()` |
| `finance.py` | `FinanceReport` | Financial overview with Net Profit and Stock metrics |
| `general.py` | `GeneralSystemReport` | Executive dashboard with Revenue, Colony Size, Connections, Progress |
| `logistics.py` | `LogisticsReport` | Logistics report with shipment tracking and `SankeyDiagram` goods flow |
| `marketing.py` | `MarketingReport` | Marketing analysis with Brand Awareness and User Acquisition metrics |

## Operating Contracts

- All report classes inherit from `BaseReport` and compose an internal `Dashboard` instance.
- `generate()` populates the dashboard sections; it is idempotent (tracked via `_generated` flag).
- `save(output_path)` calls `generate()` if not already done, then writes the dashboard HTML.
- `BaseReport.render()` produces an `<article>` with `<h1>` title and rendered sections.
- `BaseReport.to_dict()` returns `{"title": ..., "section_count": ...}`.

## Integration Points

- **Depends on**: `data_visualization.core.ui` (`Card`, `Dashboard`), `data_visualization.plots.sankey` (`SankeyDiagram` -- used by `LogisticsReport`)
- **Used by**: Dashboard export workflows, MCP `export_dashboard` tool

## Navigation

- **Parent**: [data_visualization](../README.md)
- **Root**: [Root](../../../../README.md)
