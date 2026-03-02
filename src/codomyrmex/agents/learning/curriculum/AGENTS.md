# Codomyrmex Agents -- src/codomyrmex/agents/learning/curriculum

**Version**: v1.0.0 | **Status**: Planned | **Last Updated**: March 2026

## Purpose

Placeholder subpackage for a curriculum-based learning system for agents. This directory is reserved for future implementation of structured learning sequences that guide agents through progressively complex tasks.

No Python implementation exists in this directory yet. The parent module `agents/learning/` contains the implemented `skills.py` module with `Skill` and `SkillLibrary` classes.

## Key Components

| File | Class / Function | Role |
|------|-----------------|------|
| *(none yet)* | -- | No implementation files present |

## Planned Capabilities

- Structured learning sequences for agent training
- Progressive difficulty scaling
- Curriculum-based knowledge acquisition

## Operating Contracts

- When implemented, must integrate with `agents.learning.skills.SkillLibrary` for skill tracking.
- Must follow the zero-mock policy: no stub data or placeholder implementations in production code.
- Errors must be logged via `logging_monitoring` before re-raising.
- Unimplemented paths must raise `NotImplementedError`.

## Integration Points

- **Depends on**: `agents.learning.skills` (sibling module, provides `Skill`, `SkillLibrary`)
- **Used by**: Agent training pipelines (planned)

## Navigation

- **Parent**: [../AGENTS.md](../AGENTS.md)
- **Root**: [../../../../README.md](../../../../README.md)
