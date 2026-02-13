# Personal AI Infrastructure -- Education Module

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

The Education module is the **adaptive learning engine** for the Codomyrmex ecosystem. It provides structured curriculum generation, lesson management with prerequisite tracking, and visual learning path rendering. It enables both user training and agent upskilling through a difficulty-tiered lesson framework.

## PAI Capabilities

### Curriculum Generation

Build structured learning paths with prerequisite chains:

```python
from codomyrmex.education.curriculum import Curriculum, Lesson, Difficulty

course = Curriculum(topic="Python Basics", difficulty=Difficulty.BEGINNER)
intro = Lesson(title="Variables", content="...", difficulty=Difficulty.BEGINNER, duration_minutes=30)
functions = Lesson(title="Functions", content="...", difficulty=Difficulty.BEGINNER, duration_minutes=45, prerequisites=[intro.id])

course.add_lesson(intro)
course.add_lesson(functions)
print(course.total_duration())  # 75
```

### Learning Path Visualization

Render lesson dependency graphs as Mermaid flowcharts:

```python
from codomyrmex.education.visualization import render_curriculum_path

diagram = render_curriculum_path(course)
# Returns a MermaidDiagram showing lesson prerequisite flow
```

## Key Exports

| Export | Type | Purpose |
|--------|------|---------|
| `Curriculum` | Class | Structured sequence of lessons organized by topic and difficulty |
| `Lesson` | Dataclass | Individual learning unit with content, duration, and prerequisites |
| `Difficulty` | Enum | Learning levels: BEGINNER, INTERMEDIATE, ADVANCED, EXPERT |
| `render_curriculum_path()` | Function | Mermaid flowchart of lesson dependency graph |

## PAI Algorithm Phase Mapping

| Phase | Education Module Contribution |
|-------|------------------------------|
| **OBSERVE** | Lesson difficulty and duration metrics inform skill-gap analysis |
| **PLAN** | Curriculum generation creates structured learning plans from topic requirements |
| **EXECUTE** | Lesson content delivery during agent or user training sessions |
| **VERIFY** | Prerequisite chains ensure proper knowledge sequencing |
| **LEARN** | Core module -- adaptive curricula capture and structure knowledge for progressive skill acquisition |

## Architecture Role

**Application Layer** -- Domain-specific learning management module. Depends on the `visualization` module for Mermaid diagram rendering. Has no upward dependencies from other modules.

## Navigation

- **Self**: [PAI.md](PAI.md)
- **Parent**: [../PAI.md](../PAI.md) -- Source-level PAI module map
- **Root Bridge**: [../../../PAI.md](../../../PAI.md) -- Authoritative PAI system bridge doc
- **Siblings**: [README.md](README.md) | [AGENTS.md](AGENTS.md) | [SPEC.md](SPEC.md) | [API_SPECIFICATION.md](API_SPECIFICATION.md)
