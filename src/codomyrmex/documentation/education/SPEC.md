# Education Module - Functional Specification

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

Models developer education curricula as directed acyclic graphs of lessons grouped into modules. Provides prerequisite-aware learning-path generation using Kahn's topological sort and Mermaid-based dependency visualisation.

## Architecture

Curriculum objects aggregate named modules, each containing ordered lists of Lesson dataclasses. `generate_learning_path` linearises lessons respecting prerequisite edges. `render_curriculum_path` converts the graph to a MermaidDiagram.

## Key Classes

### `Difficulty` (Enum)

| Member | Value |
|--------|-------|
| `BEGINNER` | `"beginner"` |
| `INTERMEDIATE` | `"intermediate"` |
| `ADVANCED` | `"advanced"` |
| `EXPERT` | `"expert"` |

### `Lesson` (dataclass)

| Field | Type | Description |
|-------|------|-------------|
| `title` | `str` | Unique lesson identifier |
| `objectives` | `list[str]` | Learning objectives |
| `content` | `str` | Lesson body text |
| `difficulty` | `Difficulty` | Difficulty tier |
| `duration` | `int` | Duration in minutes |
| `prerequisites` | `list[str]` | Titles of prerequisite lessons |
| `exercises` | `list[str]` | Practical exercise descriptions |

### `Curriculum`

| Method | Signature | Description |
|--------|-----------|-------------|
| `add_module` | `(name: str, lessons: list[Lesson])` | Register a module of lessons |
| `get_module` | `(name: str) -> list[Lesson]` | Retrieve lessons for a module |
| `get_modules` | `() -> dict[str, list[Lesson]]` | All modules |
| `total_duration` | `() -> int` | Sum of all lesson durations (minutes) |
| `generate_learning_path` | `() -> list[Lesson]` | Topological sort via Kahn's algorithm; raises `ValueError` on cycles |
| `export` | `(format: str) -> dict | str` | Export as `"json"` dict or `"text"` string |

### `render_curriculum_path`

| Parameter | Type | Description |
|-----------|------|-------------|
| `curriculum` | `Curriculum` | Source curriculum |
| **Returns** | `MermaidDiagram` | Directed graph of lesson dependencies |

## Dependencies

- `data_visualization.mermaid` -- `MermaidDiagram` for graph rendering.
- Standard library only otherwise (`dataclasses`, `enum`, `collections.deque`).

## Constraints

- Prerequisite references are resolved by lesson title (case-sensitive).
- Cycles in prerequisites are detected and rejected with `ValueError`.
- Empty curricula produce an empty learning path without error.

## Error Handling

| Scenario | Behaviour |
|----------|-----------|
| Cyclic prerequisites | `ValueError` raised by `generate_learning_path` |
| Unknown module name | `KeyError` from `get_module` |
| Unknown export format | Falls through; returns `None` |

## Navigation

- **Parent**: [../README.md](../README.md)
- **Siblings**: [../quality/SPEC.md](../quality/SPEC.md) | [../scripts/SPEC.md](../scripts/SPEC.md)
- **Root**: [../../../../README.md](../../../../README.md)
