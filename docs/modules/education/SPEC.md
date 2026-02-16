# Education — Functional Specification

**Module**: `codomyrmex.education`  
**Version**: v0.1.0  
**Status**: Active

## 1. Overview

Education Module for Codomyrmex.

Provides curriculum generation, interactive tutoring, and
certification / assessment capabilities.

## 2. Architecture

### Source Files

| File | Purpose |
|------|--------|
| `curriculum.py` | Learning difficulty level. |
| `visualization.py` | Generates a flowchart of the lesson dependencies. |

### Submodule Structure

- `certification/` — Certification
- `curriculum/` — Curriculum
- `tutoring/` — Tutoring

## 3. Dependencies

No internal Codomyrmex dependencies.

## 4. Public API

### Exports (`__all__`)

- `Assessment`
- `Certificate`
- `Curriculum`
- `DifficultyLevel`
- `Lesson`
- `Tutor`
- `TutoringSession`

## 5. Testing

```bash
uv run python -m pytest src/codomyrmex/tests/ -k education -v
```

All tests follow the Zero-Mock policy.

## 6. References

- [README.md](README.md) — Human-readable documentation
- [AGENTS.md](AGENTS.md) — Agent coordination guide
- [Source Code](../../../src/codomyrmex/education/)
