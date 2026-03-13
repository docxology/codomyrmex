# Agent Learning

**Module**: `codomyrmex.agents.learning` | **Category**: Core Infrastructure | **Last Updated**: March 2026

## Overview

Online learning and self-improvement system for agents. Includes feedback loops, skill extraction, performance tracking, and adaptive behavior modification.

## Purpose

Agent learning module that models reusable capabilities as `Skill` objects stored in a `SkillLibrary`. Provides tag-based search and a visualization function that charts skill distribution across tags.

## Source Module Structure

Source: [`src/codomyrmex/agents/learning/`](../../../../src/codomyrmex/agents/learning/)

### Key Files

| File | Purpose |
|:---|:---|
| [skills.py](../../../../src/codomyrmex/agents/learning/skills.py) |  |
| [visualization.py](../../../../src/codomyrmex/agents/learning/visualization.py) |  |

### Subdirectories

- `curriculum/`
- `reflection/`
- `skills/`

## Quick Start

```python
from codomyrmex.agents.learning import LearningClient

client = LearningClient()
```

## Source Documentation

| Document | Path |
|:---|:---|
| README | [learning/README.md](../../../../src/codomyrmex/agents/learning/README.md) |
| SPEC | [learning/SPEC.md](../../../../src/codomyrmex/agents/learning/SPEC.md) |
| AGENTS | [learning/AGENTS.md](../../../../src/codomyrmex/agents/learning/AGENTS.md) |
| PAI | [learning/PAI.md](../../../../src/codomyrmex/agents/learning/PAI.md) |

## Navigation

- **Parent**: [docs/agents/](../README.md)
- **Source**: [src/codomyrmex/agents/learning/](../../../../src/codomyrmex/agents/learning/)
- **Project Root**: [README.md](../../../README.md)
