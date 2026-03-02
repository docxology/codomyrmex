# Codomyrmex Agents -- src/codomyrmex/agents/learning/skills

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose

Subpackage directory for the agent skill learning system. The primary implementation lives in the parent module at `agents/learning/skills.py`, which provides the `Skill` dataclass and `SkillLibrary` class for managing learnable agent capabilities.

This directory is reserved for future expansion of the skills subsystem (e.g., skill templates, skill evaluation, skill composition).

## Key Components

| File | Class / Function | Role |
|------|-----------------|------|
| `../skills.py` | `Skill` | Dataclass representing a learnable capability with name, description, code snippet, tags, and usage tracking |
| `../skills.py` | `SkillLibrary` | Repository for storing, retrieving, and searching agent skills by name or tag |

## Operating Contracts

- `SkillLibrary.add_skill()` raises `ValueError` if a skill with the same name already exists.
- `SkillLibrary.get_skill()` returns `None` for unknown skill names (does not raise).
- `SkillLibrary.search()` filters skills by matching a single tag against each skill's tag list.
- Each `Skill` has a unique `id` (UUID) and a `created_at` timestamp set at creation time.
- Errors must be logged via `logging_monitoring` before re-raising.

## Integration Points

- **Depends on**: `dataclasses`, `datetime`, `uuid` (standard library only)
- **Used by**: `agents.learning.curriculum` (planned), `agents.learning.reflection` (planned)

## Navigation

- **Parent**: [../AGENTS.md](../AGENTS.md)
- **Root**: [../../../../README.md](../../../../README.md)
