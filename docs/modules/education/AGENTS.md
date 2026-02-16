# Education Module — Agent Coordination

## Purpose

Education Module for Codomyrmex.

Provides curriculum generation, interactive tutoring, and
certification / assessment capabilities.

## Key Capabilities

- **`Curriculum`** — Structured learning path
- **`Lesson`** — Individual educational unit
- **`Certificate`** — Proof of skill acquisition
- `curriculum/` — Path generation
- `tutoring/` — Interactive teaching
- `certification/` — Assessment and verifying

## Agent Usage Patterns

```python
from codomyrmex.education import Curriculum, Lesson

course = Curriculum(topic="Python Basics")
course.add(Lesson(title="Variables"))
```

## Key Components

| Export | Type |
|--------|------|
| `Assessment` | Public API |
| `Certificate` | Public API |
| `Curriculum` | Public API |
| `DifficultyLevel` | Public API |
| `Lesson` | Public API |
| `Tutor` | Public API |
| `TutoringSession` | Public API |

## Source Files

| File | Description |
|------|-------------|
| `curriculum.py` | Learning difficulty level. |
| `visualization.py` | Generates a flowchart of the lesson dependencies. |

## Submodules

- `certification/` — Certification
- `curriculum/` — Curriculum
- `tutoring/` — Tutoring

## Integration Points

- **Source**: [src/codomyrmex/education/](../../../src/codomyrmex/education/)
- **Spec**: [SPEC.md](SPEC.md)
- **PAI**: [PAI.md](PAI.md)

## Testing Guidelines

```bash
uv run python -m pytest src/codomyrmex/tests/ -k education -v
```

- Always use real, functional tests — no mocks (Zero-Mock policy)
- Verify all changes pass existing tests before submitting
