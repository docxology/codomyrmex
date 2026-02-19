# Composition

**Version**: v0.1.7 | **Status**: Active | **Last Updated**: February 2026

## Overview

Skill composition patterns. Provides mechanisms for combining skills into pipelines through sequential chaining, parallel execution, and conditional branching.

## Key Exports

- **`SkillComposer`** -- Builder for composing skills into workflows; provides `chain()` for sequential piping, `parallel()` for concurrent execution, and `conditional()` for branching
- **`ComposedSkill`** -- A skill created by composing other skills in either "chain" mode (output of each feeds the next) or "parallel" mode (all execute concurrently with same input, results collected by name)
- **`ConditionalSkill`** -- A skill that evaluates a condition callable and delegates to either an if-branch or else-branch skill

## Directory Contents

- `__init__.py` - All composition classes (146 lines)
- `py.typed` - PEP 561 type stub marker

## Usage

```python
from codomyrmex.skills.composition import SkillComposer

composer = SkillComposer()

# Sequential: output of skill_a feeds into skill_b
pipeline = composer.chain(skill_a, skill_b, skill_c)
result = pipeline.execute(data="input")

# Parallel: all skills run concurrently with same input
group = composer.parallel(skill_x, skill_y)
results = group.execute(data="input")  # dict of {name: result}

# Conditional: branch based on runtime condition
branched = composer.conditional(lambda **kw: kw.get("fast"), fast_skill, slow_skill)
```

## Navigation

- **Parent Module**: [skills](../README.md)
- **Project Root**: [../../../../README.md](../../../../README.md)
