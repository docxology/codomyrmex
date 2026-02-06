# Personal AI Infrastructure — Skills Module

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

The Skills module provides PAI integration for agent skill management.

## PAI Capabilities

### Skill Discovery

Find available skills:

```python
from codomyrmex.skills import SkillRegistry

registry = SkillRegistry()
skills = registry.discover("./skills/")

for skill in skills:
    print(f"{skill.name}: {skill.description}")
```

### Skill Execution

Execute skills:

```python
from codomyrmex.skills import SkillRunner

runner = SkillRunner()
result = runner.execute("code_analysis", context)
```

## PAI Integration Points

| Component | PAI Use Case |
|-----------|-------------|
| `SkillRegistry` | Discover skills |
| `SkillRunner` | Execute skills |
| `SkillBuilder` | Create skills |

## Navigation

- [README](README.md) | [AGENTS](AGENTS.md) | [SPEC](SPEC.md)
