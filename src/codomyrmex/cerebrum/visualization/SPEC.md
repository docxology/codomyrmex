# Cerebrum Visualization -- Technical Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## 1. Overview

Themed matplotlib visualization library for cerebrum analysis outputs. Renders Bayesian network graphs, case similarity charts, inference posteriors, cross-analysis concordance matrices, and multi-panel dashboard compositions.

## 2. Base Layer

### BaseNetworkVisualizer (`base.py`)

| Method | Signature | Behavior |
|--------|-----------|----------|
| `create_figure` | `() -> (Figure, Axes)` | Creates matplotlib figure at configured `figure_size` and `dpi` |
| `apply_layout` | `(G, layout, **kwargs) -> dict` | Applies networkx layout (`spring`, `circular`, `shell`) |
| `get_node_sizes` | `(G, metric, min_size, max_size) -> list` | Sizes nodes by `degree` metric, linearly scaled |
| `get_edge_widths` | `(G, min_width, max_width) -> list` | Widths from edge `weight` attribute |
| `format_title` | `(ax, title)` | Sets title with fontsize 16, bold |
| `save_figure` | `(fig, path)` | Saves with `bbox_inches="tight"`, then closes |

### BaseChartVisualizer (`base.py`)

| Method | Signature | Behavior |
|--------|-----------|----------|
| `create_figure` | `() -> (Figure, Axes)` | Creates figure at configured size |
| `format_title` | `(ax, title)` | Fontsize 14, bold |
| `format_axes_labels` | `(ax, xlabel, ylabel)` | Sets axis labels |
| `add_value_labels` | `(ax, rects, format_str)` | Annotates bar chart rectangles |
| `save_figure` | `(fig, path)` | Saves and closes |

### Theme (`theme.py`)

- `ThemeColors` dataclass: `background`, `text`, `primary`, `secondary`, `accent`, `edge_default`, `status_success/warning/error/neutral`
- `ThemeFont` dataclass: `family`, `title_size`, `label_size`, `tick_size`
- `Theme` class: `get_color_sequence(n)` via viridis colormap, `get_status_color(status)` mapping, `apply_to_axes(ax)`, `create_legend(ax, handles, labels)`

## 3. Concrete Visualizers

### ModelVisualizer (extends BaseNetworkVisualizer)

| Method | Parameters | Output |
|--------|-----------|--------|
| `visualize_network` | `network: BayesianNetwork, layout, node_size_metric, show_legend` | `Figure` with directed graph, themed nodes/edges, optional legend |
| `visualize_inference_results` | `results: dict[str, Distribution], chart_type, show_values` | `Figure` with per-variable bar charts, value labels, uniform reference line |

### CaseVisualizer (extends BaseChartVisualizer)

| Method | Parameters | Output |
|--------|-----------|--------|
| `plot_case_similarity` | `cases: list[(Case, float)], query_case, group_by, show_threshold, threshold` | `Figure` with horizontal bars, gradient coloring, threshold line |
| `plot_case_features` | `cases: list[Case], features: list[str], chart_type` | `Figure` with per-feature bar comparison across cases |

### InferenceVisualizer (extends BaseChartVisualizer)

| Method | Parameters | Output |
|--------|-----------|--------|
| `plot_inference_results` | `results: dict` | Delegates to `ModelVisualizer.visualize_inference_results()` |
| `plot_belief_evolution` | `belief_history: list[dict[str, float]], show_confidence` | `Figure` with time-series lines per state, markers, themed legend |

### ConcordanceVisualizer

| Method | Parameters | Output |
|--------|-----------|--------|
| `plot_analysis_concordance_matrix` | `cbr_results, bayesian_results, active_inference_results, pattern_ids` | `Figure` heatmap of correlation coefficients between 2-3 analysis methods |
| `plot_pattern_importance_concordance` | `importance_metrics: dict[str, dict[str, float]], pattern_ids` | `Figure` scatter plot matrix with correlation annotations |
| `plot_agreement_heatmap` | `analysis_results, pattern_ids, agreement_threshold` | `Figure` heatmap of variance-based agreement scores |

### CompositionVisualizer

| Method | Parameters | Output |
|--------|-----------|--------|
| `create_analysis_overview_dashboard` | `analysis_summary: dict, output_path` | 9-panel `GridSpec` dashboard (3x3) covering status, importance, methods, network, metrics, parts, similarity, coverage |
| `create_pattern_landscape_map` | `pattern_embeddings: dict, pattern_metadata, output_path` | 2D scatter plot with status-colored, importance-sized points and annotations |
| `create_cross_analysis_summary` | `analysis_results: dict, output_path` | Side-by-side bar chart panels for each analysis method |

## 4. Extended Base Layer

`visualization_base.py` provides `BaseVisualizer` ABC with `create_figure()`, `format_title()`, `format_axes_labels()`, `save_figure()` abstract methods, plus `BaseHeatmapVisualizer` with `create_heatmap()`.

`visualization_theme.py` provides `VisualizationTheme` with `FontConfig`, `ColorPalette`, `FigureConfig`, `AxisConfig`, `LegendConfig` dataclasses and methods: `format_axis_scientific()`, `format_axis_percentage()`, `create_status_legend()`, `create_importance_legend()`.

## 5. Dependencies

- **Internal**: `cerebrum.core.exceptions`, `cerebrum.core.cases`, `cerebrum.inference.bayesian`, `logging_monitoring`
- **External**: `matplotlib` (required), `networkx` (optional, for graph viz), `numpy`

## 6. Constraints

- All visualizers require matplotlib -- `VisualizationError` is raised if matplotlib is not installed.
- `ConcordanceVisualizer` requires at least 2 analysis methods with overlapping pattern IDs.
- Dashboard panels gracefully skip if their expected key is missing from `analysis_summary`.
- `create_analysis_overview_dashboard` does not return a `Figure` when `output_path` is provided (saves and closes instead).

## Navigation

- **Parent**: [cerebrum/](../README.md)
- **Project root**: [../../../../README.md](../../../../README.md)
