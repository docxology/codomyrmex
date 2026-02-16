# Visualization Module — Agent Coordination

## Purpose

Central Visualization Module for Codomyrmex.

Provides a unified interface for accessing visualizations across all modules
and generating comprehensive dashboards.

## Key Capabilities

- **Unified Dashboarding**: Combines charts from different domains into a single view.
- **Multi-Format Support**: Generates HTML reports.
- **Modular Adapters**: Easy integration for new modules via standard interfaces.
- **Theming**: Centralized control over look-and-feel.
- **Pluggable Plots**: Support for Scatter, Heatmap, Mermaid diagrams, and more.
- **Extensible Components**: Reusable UI components like Cards and Tables.

## Agent Usage Patterns

```python
from codomyrmex.visualization import GeneralSystemReport

# Create and save a report
report = GeneralSystemReport()
report_path = report.save("my_dashboard.html")
print(f"Dashboard generated at: {report_path}")
```

## Key Components

| Export | Type |
|--------|------|
| `Dashboard` | Public API |
| `Grid` | Public API |
| `Theme` | Public API |
| `Plot` | Public API |
| `ScatterPlot` | Public API |
| `Heatmap` | Public API |
| `MermaidDiagram` | Public API |
| `BarPlot` | Public API |
| `LinePlot` | Public API |
| `Histogram` | Public API |
| `PieChart` | Public API |
| `BoxPlot` | Public API |
| `AreaPlot` | Public API |
| `ViolinPlot` | Public API |
| `RadarChart` | Public API |

## Submodules

- `components/` — Components
- `core/` — Core
- `plots/` — Plots
- `reports/` — Reports

## Internal Dependencies

- `codomyrmex.model_context_protocol`

## Integration Points

- **Source**: [src/codomyrmex/visualization/](../../../src/codomyrmex/visualization/)
- **Spec**: [SPEC.md](SPEC.md)
- **PAI**: [PAI.md](PAI.md)

## Testing Guidelines

```bash
uv run python -m pytest src/codomyrmex/tests/ -k visualization -v
```

- Always use real, functional tests — no mocks (Zero-Mock policy)
- Verify all changes pass existing tests before submitting
