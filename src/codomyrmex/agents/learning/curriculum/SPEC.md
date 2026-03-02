# Curriculum -- Technical Specification

**Version**: v1.0.0 | **Status**: Planned | **Last Updated**: March 2026

## Overview

Reserved subpackage for curriculum-based agent learning. No implementation exists yet. When built, this module will define structured learning sequences that guide agents through progressively complex tasks.

## Architecture

The intended design is a curriculum engine that sequences learning objectives and tracks completion. It will integrate with the sibling `skills` module (`Skill`, `SkillLibrary`) for persistent skill tracking.

## Planned Interface

### `Curriculum` (planned)

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `add_lesson` | `lesson: Lesson` | `None` | Register a lesson in the curriculum |
| `next_lesson` | `agent_id: str` | `Lesson` | Get the next lesson for an agent |
| `mark_complete` | `agent_id: str, lesson_id: str` | `None` | Record lesson completion |

## Dependencies

- **Internal**: `agents.learning.skills` (sibling -- `Skill`, `SkillLibrary`)
- **External**: None planned

## Constraints

- No implementation exists; this is a documentation placeholder for a planned module.
- Zero-mock: when implemented, real data only. `NotImplementedError` for unimplemented paths.
- Must not introduce circular dependencies with parent `agents.learning` package.

## Error Handling

- All errors logged before propagation.
- Unimplemented features must raise `NotImplementedError`, never return stub data.
