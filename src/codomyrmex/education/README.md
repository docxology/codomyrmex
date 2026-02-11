# Education Module

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

Comprehensive learning management system for training users and upskilling agents. Features curriculum generation, interactive tutoring, and skill certification.

## Installation

```bash
uv pip install codomyrmex
```

## Key Exports

### Learning

- **`Curriculum`** — Structured learning path
- **`Lesson`** — Individual educational unit
- **`Certificate`** — Proof of skill acquisition

### Submodules

- `curriculum/` — Path generation
- `tutoring/` — Interactive teaching
- `certification/` — Assessment and verifying

## Quick Start

```python
from codomyrmex.education import Curriculum, Lesson

course = Curriculum(topic="Python Basics")
course.add(Lesson(title="Variables"))
```

## Navigation

- [SPEC](SPEC.md) | [AGENTS](AGENTS.md) | [Parent](../README.md)
