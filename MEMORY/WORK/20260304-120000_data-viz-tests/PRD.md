---
task: Write comprehensive zero-mock data_visualization tests
slug: 20260304-120000_data-viz-tests
effort: Advanced
phase: complete
progress: 28/28
mode: algorithm
started: 2026-03-04T12:00:00
updated: 2026-03-04T12:00:00
---

## Context

Add 60+ zero-mock test methods to `src/codomyrmex/tests/unit/data_visualization/` to close 57 open desloppify test_coverage gaps. Key targets by coverage:

- `dashboard_builder.py` — 0% (64 stmts)
- `dashboard_export.py` — 0% (39 stmts)
- `mcp_tools.py` — 0% (31 stmts)
- `export.py` — 47% (30 uncovered stmts)
- `_compat.py` — 24% (13 uncovered stmts)
- `mermaid/__init__.py` — 83% (31 uncovered stmts)
- `core/ui.py` — 82% (9 uncovered stmts)
- `core/theme.py` — 91% (4 uncovered stmts)
- `engines/plotter.py` — 81% (6 uncovered stmts)
- `charts/line_plot.py` — 83% (9 uncovered stmts)
- `charts/pie_chart.py` — 89% (5 uncovered stmts)

### Risks

- matplotlib Agg backend must be set before any import that triggers display
- Some tests may hit OS-level file system; use tmp_path
- MCP tool tests call real chart factories — need minimal valid inputs
- export_dashboard calls generate_report which writes HTML files; need tmp_path

## Criteria

- [x] ISC-1: TestDashboardBuilder class created with 8+ test methods
- [x] ISC-2: DashboardBuilder.build() result structure validated (title, panels, annotations, templating, refresh)
- [x] ISC-3: DashboardBuilder.to_json() returns valid JSON string
- [x] ISC-4: Panel.thresholds field renders correctly in build() output
- [x] ISC-5: Panel.unit field renders fieldConfig in build() output
- [x] ISC-6: DashboardBuilder.add_annotation() adds annotation to output
- [x] ISC-7: DashboardBuilder.set_variable() adds template variable to output
- [x] ISC-8: DashboardBuilder.set_refresh() updates refresh interval
- [x] ISC-9: TestDashboardExport class created with 8+ test methods
- [x] ISC-10: DashboardExporter.export() returns dict with dashboard key
- [x] ISC-11: DashboardExporter.add_panel() increments panel_count
- [x] ISC-12: DashboardExporter.agent_dashboard() returns 4-panel preset
- [x] ISC-13: dashboard_export.Panel.to_dict() includes title, type, targets, fieldConfig
- [x] ISC-14: Dashboard.to_dict() nests panels under dashboard key
- [x] ISC-15: TestMcpTools class created with 6+ test methods
- [x] ISC-16: generate_chart returns status=success for valid bar chart input
- [x] ISC-17: generate_chart returns status=error for unsupported chart type
- [x] ISC-18: generate_chart saves output file when output_path provided
- [x] ISC-19: export_dashboard returns status=success for general report
- [x] ISC-20: TestChartExporter class created with 5+ test methods
- [x] ISC-21: ChartExporter.export() saves PNG file to tmp_path
- [x] ISC-22: ChartExporter.export_multi() saves multiple format files
- [x] ISC-23: ChartExporter.export_html() creates HTML file via SVG fallback
- [x] ISC-24: TestCompatShim class tests PERFORMANCE_MONITORING_AVAILABLE flag
- [x] ISC-25: TestMermaidDiagram class created with 5+ test methods covering flowchart/sequence rendering
- [x] ISC-26: TestCoreUIComponents class created with 5+ test methods covering Card, Table, Dashboard
- [x] ISC-27: TestEnginesPlotter class created covering Plotter.bar_chart, line_plot, scatter_plot, histogram, pie_chart, heatmap
- [x] ISC-28: All 60+ new tests pass with zero failures

## Decisions

## Verification
