# Skill Templates

> Codomyrmex v1.1.4 | March 2026

## Overview

The `templates/` directory provides YAML-based starter templates for authoring custom skills within the codomyrmex skill system. Each template defines patterns, anti-patterns, validations, and sharp edges for a specific domain of software development practice.

Templates are consumed by the `SkillsManager` and `SkillLoader` when creating new custom skills via the `skills_add_custom` MCP tool or the `SkillsManager.add_custom_skill()` API.

## PAI Integration

| PAI Phase | Role |
|-----------|------|
| PLAN | Templates guide skill authoring during planning |
| BUILD | Patterns from templates enforce standards during implementation |
| VERIFY | Validation rules from templates drive automated quality checks |

## Available Templates

| Template | File | Purpose |
|----------|------|---------|
| Code Review | `code_review.yaml` | Style enforcement, complexity thresholds, naming conventions, security anti-patterns |
| Documentation | `documentation.yaml` | RASP compliance, API specs, docstring standards, changelog entries |
| Testing | `testing.yaml` | Unit test structure, fixture design, parameterization, zero-mock strategies |

## Template Structure

Each YAML template follows a consistent schema:

```yaml
description: >
  High-level purpose of the skill domain.

patterns:
  - name: pattern_name
    description: When and how to apply this pattern.
    example: |
      # Code example demonstrating the pattern

anti_patterns:
  - name: anti_pattern_name
    why_bad: Explanation of why this is harmful.
    example: |
      # Bad and good examples

validations:
  - "Rule that must hold true"

sharp_edges:
  - "Warning about subtle pitfalls"
```

## Quick Start

```python
from codomyrmex.skills import get_skills_manager

mgr = get_skills_manager()
mgr.initialize()

# List available templates
import yaml
from pathlib import Path

templates_dir = Path("src/codomyrmex/skills/skills/templates")
for template_file in templates_dir.glob("*.yaml"):
    with open(template_file) as f:
        template = yaml.safe_load(f)
    print(f"{template_file.stem}: {template['description'][:60]}...")
```

## Architecture

```
skills/skills/templates/
    code_review.yaml      # Code review patterns and anti-patterns
    documentation.yaml    # Documentation standards and RASP compliance
    testing.yaml          # Testing patterns and zero-mock strategies
    README.md             # This file
    AGENTS.md             # Agent coordination guide
    SPEC.md               # Technical specification
```

## Testing

Templates are validated by the skills module test suite:

```bash
uv run pytest src/codomyrmex/tests/unit/skills/ -k "template"
```

## Navigation

- Parent: [skills module](../../README.md)
- Related: [skills MCP tools](../../mcp_tools.py)
- Root: [codomyrmex](../../../../../README.md)
