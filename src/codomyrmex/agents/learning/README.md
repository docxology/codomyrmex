# Agent Learning Module

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

Implements the learning loop for autonomous agents. Enables skill acquisition, performance reflection, and curriculum-based improvement.

## Installation

```bash
uv add codomyrmex
```

## Key Exports

### Learning

- **`Skill`** — Reusable capability unit
- **`Reflection`** — Post-action analysis
- **`LessonPlan`** — Targeted improvement strategy

### Submodules

- `skills/` — Extraction and storage
- `reflection/` — Self-evaluation logic
- `curriculum/` — Automated difficulty scaling

## Quick Start

```python
from codomyrmex.agents.learning import Skill, Reflection

reflection = Reflection(action_log=logs)
new_skill = reflection.extract_skill()
```

## Navigation

- [SPEC](SPEC.md) | [AGENTS](AGENTS.md) | [Parent](../README.md)
