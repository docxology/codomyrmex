# Education Module - Agent Coordination

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose

Provides curriculum modelling and learning-path generation for developer education workflows. Agents use this module to build structured lesson sequences, enforce prerequisite ordering via topological sort, and render visual dependency graphs.

## Key Components

| File | Class / Function | Role |
|------|-----------------|------|
| `curriculum.py` | `Difficulty` | Enum: BEGINNER, INTERMEDIATE, ADVANCED, EXPERT |
| `curriculum.py` | `Lesson` | Dataclass holding title, objectives, content, difficulty, duration, prerequisites, exercises |
| `curriculum.py` | `Curriculum` | Container managing modules of lessons; `generate_learning_path` uses Kahn's algorithm for topological sort |
| `visualization.py` | `render_curriculum_path` | Converts a Curriculum into a MermaidDiagram showing lesson dependencies |
| `__init__.py` | (exports) | Re-exports `Curriculum`, `Difficulty`, `Lesson`; optional imports for `Tutor`, `TutoringSession`, `Assessment`, `Certificate` |

## Operating Contracts

- Lesson prerequisites must reference valid lesson titles within the same curriculum; `generate_learning_path` raises `ValueError` on cycles.
- Duration values are in minutes; `total_duration` aggregates across all modules.
- Export formats: `export("json")` returns serialisable dict; `export("text")` returns human-readable string.
- Agents must not bypass prerequisite validation when constructing paths.

## Integration Points

- `data_visualization` -- `render_curriculum_path` produces `MermaidDiagram` objects consumable by mermaid renderers.
- `documentation/quality` -- curriculum content can be audited for completeness via the quality assessment pipeline.

## Navigation

- **Parent**: [../README.md](../README.md)
- **Siblings**: [../quality/AGENTS.md](../quality/AGENTS.md) | [../scripts/AGENTS.md](../scripts/AGENTS.md)
- **Root**: [../../../../README.md](../../../../README.md)
