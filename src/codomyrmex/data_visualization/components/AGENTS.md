# Codomyrmex Agents -- src/codomyrmex/data_visualization/components

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose

HTML UI components for building dashboards and reports. Each component is a `@dataclass` subclass of `BaseComponent` with a `render() -> str` method that produces self-contained HTML. Components cover alerts, badges, chat bubbles, heatmap tables, JSON viewers, media (image/video), progress bars, stat boxes, text/code blocks, and timelines.

## Key Components

| File | Class | Role |
|------|-------|------|
| `_base.py` | `BaseComponent` | Abstract base dataclass with `render()`, `to_dict()`, `css_class`, and `style` |
| `alert.py` | `Alert` | Notification alert with `message` and `level` (success/warning/danger/info) |
| `badge.py` | `Badge` | Inline label badge with `label` and `color` (named or hex) |
| `chat_bubble.py` | `ChatBubble` | Chat message bubble with `message`, `role`, and `timestamp` |
| `heatmap_table.py` | `HeatmapTable` | HTML table with colour-coded cells based on numeric value intensity |
| `json_view.py` | `JsonView` | Collapsible JSON viewer using `<details>/<summary>` |
| `media.py` | `Image`, `Video` | Image with optional caption; video with autoplay/controls toggles |
| `progress.py` | `ProgressBar` | Progress bar with `value`, `max_value`, and optional `label` |
| `statbox.py` | `StatBox` | KPI stat box with `label`, `value`, `delta`, and `direction` (up/down) |
| `text.py` | `TextBlock`, `CodeBlock` | Plain/markdown text block; syntax-highlighted code block |
| `timeline.py` | `TimelineEvent`, `Timeline` | Single timeline event and a container that renders a list of events |

## Operating Contracts

- All components inherit from `BaseComponent` and implement `render() -> str`.
- `render()` returns valid, self-contained HTML fragments (no external CSS dependencies).
- `HeatmapTable` computes min/max colour scaling automatically from numeric cell values.
- `Alert` and `Badge` use internal colour maps for named levels/colours.
- `__str__()` delegates to `render()` on all components for direct string interpolation.

## Integration Points

- **Depends on**: Python stdlib only (`dataclasses`, `json`)
- **Used by**: `data_visualization.core.ui` (Dashboard composition), `data_visualization.reports` (report sections)

## Navigation

- **Parent**: [data_visualization](../README.md)
- **Root**: [Root](../../../../README.md)
