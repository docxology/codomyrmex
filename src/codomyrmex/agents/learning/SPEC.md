# Learning -- Technical Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

Agent learning module that models reusable capabilities as `Skill` objects stored in a `SkillLibrary`. Provides tag-based search and a visualization function that charts skill distribution across tags.

## Architecture

Simple repository pattern: `SkillLibrary` holds `Skill` dataclasses in a name-keyed dict. The `visualization` module aggregates tag frequencies via `collections.Counter` and renders a `BarChart` from the `data_visualization` module.

## Key Classes

### `Skill`

| Field | Type | Description |
|-------|------|-------------|
| `name` | `str` | Unique skill identifier |
| `description` | `str` | Human-readable description of the capability |
| `code_snippet` | `str` | Reusable code associated with the skill |
| `tags` | `list[str]` | Categorization tags for search |
| `usage_count` | `int` | Number of times the skill has been applied |
| `created_at` | `datetime` | Creation timestamp (defaults to `datetime.now()`) |
| `id` | `UUID` | Auto-generated UUID4 |

### `SkillLibrary`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `add_skill` | `skill: Skill` | `None` | Adds a skill; raises `ValueError` on name collision |
| `get_skill` | `name: str` | `Skill \| None` | Retrieves a skill by name |
| `search` | `tag: str` | `list[Skill]` | Returns all skills containing the given tag |

### `plot_skill_distribution`

| Parameter | Type | Returns | Description |
|-----------|------|---------|-------------|
| `library` | `SkillLibrary` | `str` | Renders a bar chart of tag frequencies as HTML/SVG |

## Dependencies

- **Internal**: `codomyrmex.data_visualization.charts.bar_chart` (`BarChart`)
- **External**: Standard library (`dataclasses`, `datetime`, `uuid`, `collections`)

## Constraints

- Skill names must be unique within a `SkillLibrary` instance.
- Tag search is exact string match within the `tags` list; no fuzzy or partial matching.
- `plot_skill_distribution` accesses `library._skills` directly; changing the internal storage structure would break visualization.
- Zero-mock: real data only, `NotImplementedError` for unimplemented paths.

## Error Handling

- `ValueError` raised by `add_skill` when a duplicate skill name is detected.
- All errors logged before propagation.
