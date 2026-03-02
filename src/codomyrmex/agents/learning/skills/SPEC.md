# Skills -- Technical Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

Defines the `Skill` dataclass and `SkillLibrary` repository for managing learnable agent capabilities. Skills are code snippets tagged for searchability, with usage tracking and unique identification.

## Architecture

Simple repository pattern: `SkillLibrary` stores `Skill` instances in a name-keyed dictionary. No persistence layer -- state is in-memory only. The design is intentionally minimal to serve as a foundation for curriculum and reflection modules.

## Key Classes

### `Skill`

Dataclass representing a single learnable capability.

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `name` | `str` | *(required)* | Unique human-readable skill name |
| `description` | `str` | *(required)* | What the skill does |
| `code_snippet` | `str` | *(required)* | Executable code demonstrating the skill |
| `tags` | `list[str]` | `[]` | Searchable tags for categorization |
| `usage_count` | `int` | `0` | Number of times the skill has been invoked |
| `created_at` | `datetime` | `datetime.now()` | Timestamp of skill creation |
| `id` | `UUID` | `uuid4()` | Unique identifier |

### `SkillLibrary`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `add_skill` | `skill: Skill` | `None` | Add a skill; raises `ValueError` if name exists |
| `get_skill` | `name: str` | `Skill or None` | Retrieve a skill by name |
| `search` | `tag: str` | `list[Skill]` | Find all skills containing the given tag |

## Dependencies

- **Internal**: None (standalone within `agents.learning`)
- **External**: Standard library only (`dataclasses`, `datetime`, `uuid`)

## Constraints

- Skill names must be unique within a `SkillLibrary` instance.
- No persistence: library state is lost when the process exits.
- Zero-mock: real data only, `NotImplementedError` for unimplemented paths.

## Error Handling

- `add_skill` raises `ValueError` for duplicate names.
- `get_skill` returns `None` for missing skills (no exception).
- All errors logged before propagation.
