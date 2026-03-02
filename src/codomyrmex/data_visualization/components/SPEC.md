# Components -- Technical Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

A library of HTML-rendering UI components for dashboards and reports. Each component is a Python `@dataclass` inheriting from `BaseComponent`, producing self-contained HTML fragments via `render()`. No external CSS or JavaScript is required.

## Architecture

All components follow the dataclass-with-render pattern:

```
BaseComponent (@dataclass)
  ├── css_class: str
  ├── style: dict[str, str]
  ├── render() -> str        # Returns HTML fragment
  ├── to_dict() -> dict      # Serialization
  └── __str__() -> render()
```

Subclasses add domain-specific fields (e.g., `Alert.level`, `StatBox.delta`) and override `render()`.

## Key Classes

### `BaseComponent`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `render` | -- | `str` | Default: `<div>` with class name |
| `to_dict` | -- | `dict` | `{"type": class_name}` |

### `Alert`

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `message` | `str` | `""` | Alert text content |
| `level` | `str` | `"info"` | One of: success, warning, danger, info |

### `Badge`

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `label` | `str` | `""` | Badge text |
| `color` | `str` | `"#3B82F6"` | Named key (success/warning/danger/info/primary) or hex code |

### `HeatmapTable`

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `headers` | `list` | `[]` | Column headers |
| `rows` | `list` | `[]` | 2D list of cell values; numeric cells get colour-coded backgrounds |
| `title` | `str` | `""` | Optional table caption |

### `StatBox`

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `label` | `str` | `""` | Metric name |
| `value` | `str` | `""` | Metric value |
| `delta` | `str` | `""` | Change indicator text |
| `direction` | `str` | `""` | `"up"` (green) or `"down"` (red) |

### `Timeline`

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `events` | `list[TimelineEvent]` | `[]` | Ordered list of `TimelineEvent` instances |

### Other Components

- **`ChatBubble`**: `message`, `role` (user/assistant alignment), `timestamp`
- **`JsonView`**: `data` (dict), `collapsed` (bool), `label`
- **`Image`**: `src`, `alt`, `caption`
- **`Video`**: `src`, `autoplay`, `controls`
- **`ProgressBar`**: `value`, `max_value`, `label`
- **`TextBlock`**: `content`, `is_markdown`
- **`CodeBlock`**: `code`, `language`

## Dependencies

- **Internal**: None (pure Python dataclasses)
- **External**: None

## Constraints

- Components produce inline-styled HTML; no external stylesheets.
- `HeatmapTable` colour scaling uses linear interpolation between min and max values with rgba alpha.
- Zero-mock: all `render()` calls produce real HTML; `NotImplementedError` for unimplemented paths.

## Error Handling

- No exceptions are raised by `render()` methods; empty fields result in empty HTML elements.
- `HeatmapTable` handles empty `rows` gracefully (division-by-zero guarded with `rng = max_v - min_v or 1`).
