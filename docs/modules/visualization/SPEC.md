# Visualization — Functional Specification

**Module**: `codomyrmex.visualization`  
**Version**: v0.1.0  
**Status**: Active

## 1. Overview

Central Visualization Module for Codomyrmex.

Provides a unified interface for accessing visualizations across all modules
and generating comprehensive dashboards.

## 2. Architecture

### Submodule Structure

- `components/` — Components
- `core/` — Core
- `plots/` — Plots
- `reports/` — Reports

## 3. Dependencies

### Internal

- `codomyrmex.model_context_protocol`

## 4. Public API

### Exports (`__all__`)

- `Dashboard`
- `Grid`
- `Theme`
- `Plot`
- `ScatterPlot`
- `Heatmap`
- `MermaidDiagram`
- `BarPlot`
- `LinePlot`
- `Histogram`
- `PieChart`
- `BoxPlot`
- `AreaPlot`
- `ViolinPlot`
- `RadarChart`
- `CandlestickChart`
- `GanttChart`
- `FunnelChart`
- `SankeyDiagram`
- `WordCloud`
- `ConfusionMatrix`
- `TreeMap`
- `NetworkGraph`
- `Card`
- `Table`
- `Image`
- `Video`
- `TextBlock`
- `CodeBlock`
- `Badge`
- `Alert`
- `ProgressBar`
- `Timeline`
- `TimelineEvent`
- `StatBox`
- `ChatBubble`
- `JsonView`
- `HeatmapTable`
- `Report`
- `GeneralSystemReport`
- `FinanceReport`
- `MarketingReport`
- `LogisticsReport`
- `generate_report`

## 5. Testing

```bash
uv run python -m pytest src/codomyrmex/tests/ -k visualization -v
```

All tests follow the Zero-Mock policy.

## 6. References

- [README.md](README.md) — Human-readable documentation
- [AGENTS.md](AGENTS.md) — Agent coordination guide
- [Source Code](../../../src/codomyrmex/visualization/)
