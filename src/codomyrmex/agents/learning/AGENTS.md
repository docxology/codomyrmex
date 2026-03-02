# Codomyrmex Agents -- src/codomyrmex/agents/learning

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose

Provides mechanisms for agents to acquire, store, and query reusable skills. The module defines a `Skill` dataclass representing a learnable capability with associated code and tags, a `SkillLibrary` repository for adding, retrieving, and tag-searching skills, and a visualization helper that renders bar charts of skill distribution by tag.

## Key Components

| File | Class / Function | Role |
|------|-----------------|------|
| `skills.py` | `Skill` | Dataclass: name, description, code_snippet, tags, usage_count, UUID id |
| `skills.py` | `SkillLibrary` | In-memory skill repository with `add_skill`, `get_skill`, `search` by tag |
| `visualization.py` | `plot_skill_distribution` | Renders a `BarChart` of skill counts grouped by tag using `data_visualization.charts` |

## Operating Contracts

- `SkillLibrary.add_skill` raises `ValueError` if a skill with the same name already exists; names are unique keys.
- `SkillLibrary.search` performs exact tag membership checks (tag must appear in `Skill.tags` list).
- `plot_skill_distribution` accesses `library._skills` directly to aggregate tag counts via `collections.Counter`.
- Each `Skill` receives a `uuid4` on creation; `created_at` defaults to `datetime.now()`.
- Errors must be logged via `logging_monitoring` before re-raising.

## Integration Points

- **Depends on**: `codomyrmex.data_visualization.charts.bar_chart` (`BarChart`)
- **Used by**: Agent learning pipelines, skill cataloging workflows

## Navigation

- **Parent**: [agents](../README.md)
- **Root**: [codomyrmex](../../../../README.md)
