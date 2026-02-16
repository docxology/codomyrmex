# Education Module Documentation

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

Comprehensive learning management system for training users and upskilling agents. Features curriculum generation, interactive tutoring, and skill certification.

## Installation

```bash
uv pip install codomyrmex
```

## Key Features

- **`Curriculum`** -- Structured learning path generation.
- **`Lesson`** -- Individual educational unit within a curriculum.
- **`Certificate`** -- Proof of skill acquisition after assessment.

## Submodules

| Submodule | Description |
|-----------|-------------|
| `curriculum` | Learning path generation |
| `tutoring` | Interactive teaching |
| `certification` | Assessment and verification |

## Quick Start

```python
from codomyrmex.education import Curriculum

course = Curriculum(topic="Python Basics")
course.add(Lesson(title="Variables"))
```

## API Reference

### Classes

| Class | Description |
|-------|-------------|
| `Curriculum` | Structured learning path |
| `Lesson` | Individual educational unit |
| `Certificate` | Proof of skill acquisition |

## Directory Contents

| File | Description |
|------|-------------|
| `README.md` | This documentation |
| `AGENTS.md` | Agent coordination guide |
| `SPEC.md` | Technical specification |

## Testing

```bash
uv run python -m pytest src/codomyrmex/tests/ -k education -v
```

## Navigation

- **Source**: [src/codomyrmex/education/](../../../src/codomyrmex/education/)
- **API Spec**: [API_SPECIFICATION.md](../../../src/codomyrmex/education/API_SPECIFICATION.md)
- **MCP Spec**: [MCP_TOOL_SPECIFICATION.md](../../../src/codomyrmex/education/MCP_TOOL_SPECIFICATION.md)
- **Parent**: [Modules](../README.md)
