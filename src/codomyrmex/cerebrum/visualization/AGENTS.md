# Cerebrum Visualization -- Agent Coordination

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose

Visualization toolkit for the cerebrum subsystem. Provides themed matplotlib-based renderers for Bayesian networks, case similarity charts, inference results, cross-analysis concordance, and multi-panel dashboard compositions.

## Key Components

| File | Class | Role |
|------|-------|------|
| `base.py` | `BaseNetworkVisualizer` | Graph layout, node sizing by degree, edge width by weight |
| `base.py` | `BaseChartVisualizer` | Figure creation, axis formatting, value labels |
| `theme.py` | `ThemeColors`, `ThemeFont`, `Theme` | Color palette, font settings, `get_status_color()`, `apply_to_axes()` |
| `core.py` | `ModelVisualizer(BaseNetworkVisualizer)` | `visualize_network()` for `BayesianNetwork`, `visualize_inference_results()` for posterior bars |
| `core.py` | `CaseVisualizer(BaseChartVisualizer)` | `plot_case_similarity()` with gradient colors and thresholds, `plot_case_features()` |
| `core.py` | `InferenceVisualizer(BaseChartVisualizer)` | `plot_inference_results()`, `plot_belief_evolution()` over time steps |
| `concordance.py` | `ConcordanceVisualizer` | `plot_analysis_concordance_matrix()` (CBR vs Bayesian vs Active Inference), `plot_pattern_importance_concordance()`, `plot_agreement_heatmap()` |
| `composition.py` | `CompositionVisualizer` | `create_analysis_overview_dashboard()` (9-panel GridSpec), `create_pattern_landscape_map()` (2D embedding), `create_cross_analysis_summary()` |
| `visualization_base.py` | `BaseVisualizer` ABC, `BaseHeatmapVisualizer` | Extended base classes with theme-integrated heatmap creation |
| `visualization_theme.py` | `VisualizationTheme`, `FontConfig`, `ColorPalette`, `FigureConfig`, `AxisConfig`, `LegendConfig` | Full theme system with `format_axis_scientific()`, `format_axis_percentage()`, status/importance legends |

## Architecture

Two parallel abstraction levels exist:

1. **Simple base** (`base.py` + `theme.py`) -- lightweight `BaseNetworkVisualizer`, `BaseChartVisualizer`, `Theme` with minimal configuration.
2. **Extended base** (`visualization_base.py` + `visualization_theme.py`) -- full `BaseVisualizer` ABC hierarchy with `BaseHeatmapVisualizer`, `VisualizationTheme` dataclass system.

The concrete visualizers in `core.py`, `concordance.py`, and `composition.py` import from the simple base layer.

## Agent Operating Contract

1. **Single model visualization** -- Use `ModelVisualizer.visualize_network(network)` for Bayesian network topology. Use `ModelVisualizer.visualize_inference_results(results)` for posterior distribution bar charts.
2. **Case analysis** -- Use `CaseVisualizer.plot_case_similarity(cases)` to render ranked similarity scores with gradient coloring and configurable thresholds.
3. **Belief tracking** -- Use `InferenceVisualizer.plot_belief_evolution(belief_history)` to plot state probability trajectories over time.
4. **Cross-method comparison** -- Use `ConcordanceVisualizer.plot_analysis_concordance_matrix()` to compare CBR, Bayesian, and active inference results via correlation heatmaps.
5. **Dashboard assembly** -- Use `CompositionVisualizer.create_analysis_overview_dashboard(summary)` for 9-panel overview. Provide keys: `status_distribution`, `importance_distribution`, `method_summary`, `network_summary`, `key_metrics`, `part_distribution`, `similarity_distribution`, `coverage`.
6. **Theming** -- All visualizers accept an optional `theme` parameter. Use `get_default_theme()` for the shared default. The `Theme.get_status_color(status)` method maps statuses to colors consistently.
7. **Output** -- All plot methods return a `matplotlib.figure.Figure`. Pass `output_path` to composition methods to save to disk and auto-close the figure.

## Dependencies

- **Internal**: `cerebrum.core.exceptions` (`VisualizationError`), `cerebrum.core.cases` (`Case`), `cerebrum.inference.bayesian` (`BayesianNetwork`), `logging_monitoring`
- **External**: `matplotlib`, `networkx`, `numpy`

## Testing Guidance

- Verify figure creation does not raise with minimal valid inputs (empty graphs, single-point distributions).
- Test `ConcordanceVisualizer` with 2 and 3 analysis methods to confirm correlation matrix shape.
- Test `CompositionVisualizer` with partial `analysis_summary` dicts (missing keys should not crash).
- No mocks -- instantiate real visualizer objects and verify returned `Figure` type.

## Navigation

- **Parent**: [cerebrum/](../README.md)
- **Sibling**: [inference/](../inference/AGENTS.md)
- **Project root**: [../../../../README.md](../../../../README.md)
