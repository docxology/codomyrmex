# Skill Templates - Agent Coordination

> Codomyrmex v1.0.8 | March 2026

## Overview

Skill templates provide YAML-based starter patterns that agents use when authoring custom skills. The three bundled templates (code_review, documentation, testing) encode best practices from the codomyrmex zero-mock policy and RASP documentation standard.

## Key Files

| File | Purpose |
|------|---------|
| `code_review.yaml` | Naming conventions, function size limits, anti-patterns (bare except, mutable defaults) |
| `documentation.yaml` | RASP coverage requirements, Google-style docstrings, changelog enforcement |
| `testing.yaml` | Arrange/Act/Assert structure, parametrize patterns, mock-free verification |

## MCP Tools Available

Templates are accessed indirectly through the skills module MCP tools:

| Tool | Relevance |
|------|-----------|
| `skills_list` | Lists skills including template-based custom skills |
| `skills_get` | Retrieves a specific skill by category and name |
| `skills_add_custom` | Creates new skills using templates as starting points |
| `skills_search` | Searches across all skills including template-derived ones |
| `skills_get_categories` | Lists categories available for template-based skills |

## Agent Instructions

1. **Use templates as starting points** -- read the relevant YAML template before authoring a custom skill to inherit proven patterns and anti-patterns.
2. **Preserve the schema** -- custom skills must follow the same `patterns` / `anti_patterns` / `validations` / `sharp_edges` structure defined in templates.
3. **Respect the zero-mock policy** -- the `testing.yaml` template explicitly prohibits mock usage; agents must not override this when creating test-related skills.
4. **Validate RASP compliance** -- when creating documentation skills, ensure the `documentation.yaml` template's validation rules (README.md exists, docstrings present) are inherited.

## Operating Contracts

- Templates are read-only reference files; agents create custom skills, never modify templates directly.
- All template YAML files must parse cleanly with `yaml.safe_load()`.
- Template patterns include `example` fields with runnable code snippets.

## Common Patterns

```python
# Reading a template for skill authoring
import yaml
from pathlib import Path

template_path = Path("src/codomyrmex/skills/skills/templates/code_review.yaml")
with open(template_path) as f:
    template = yaml.safe_load(f)

# Extract patterns for a new skill
for pattern in template["patterns"]:
    print(f"Pattern: {pattern['name']} - {pattern['description']}")
```

## PAI Agent Role Access Matrix

| Agent Role | Access Level | Typical Use |
|------------|-------------|-------------|
| Engineer | Read | Reference patterns during implementation |
| Architect | Read | Design skill schemas aligned with templates |
| QATester | Read | Validate skills follow template anti-pattern rules |

## Navigation

- Parent: [skills module](../../README.md)
- Related: [skills MCP tools](../../mcp_tools.py)
- Root: [codomyrmex](../../../../../README.md)
