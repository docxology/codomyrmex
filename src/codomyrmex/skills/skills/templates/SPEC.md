# Skill Templates - Technical Specification

> Codomyrmex v1.1.4 | March 2026

## Overview

This specification defines the YAML schema and behavioral contracts for skill templates used by the codomyrmex skills module. Templates serve as authoritative starting points when agents or users create custom skills.

## Design Principles

1. **Declarative over imperative** -- templates are YAML data, not executable code. Code appears only in `example` fields as documentation.
2. **Composable** -- each template covers a single domain (code review, documentation, testing) and can be combined with upstream skills from vibeship-spawner-skills.
3. **Zero-mock aligned** -- testing templates explicitly prohibit mock usage, aligning with the project-wide zero-mock policy.

## Architecture

```
templates/
    code_review.yaml      # Code quality patterns
    documentation.yaml    # RASP documentation patterns
    testing.yaml          # Test authoring patterns
```

Templates are loaded by `SkillsManager` via the `SkillLoader` class, which scans the `skills/templates/` directory alongside upstream and custom skill directories.

## Functional Requirements

### Template YAML Schema

Every template YAML file must contain:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `description` | string | Yes | Multi-line description of the skill domain |
| `patterns` | list[Pattern] | Yes | Recommended patterns with examples |
| `anti_patterns` | list[AntiPattern] | Yes | Patterns to avoid with explanations |
| `validations` | list[string] | Yes | Rules that must hold true for compliant code |
| `sharp_edges` | list[string] | Yes | Subtle pitfalls and warnings |

### Pattern Object

| Field | Type | Required |
|-------|------|----------|
| `name` | string | Yes |
| `description` | string | Yes |
| `example` | string (multiline) | No |
| `threshold` | number | No |

### AntiPattern Object

| Field | Type | Required |
|-------|------|----------|
| `name` | string | Yes |
| `why_bad` | string | Yes |
| `example` | string (multiline) | No |

## Interface Contracts

- Templates are consumed via `yaml.safe_load()` -- no custom YAML tags permitted.
- The `SkillsManager.add_custom_skill(category, name, skill_data)` method accepts dictionaries that follow this template schema.
- Templates do not define `id`, `category`, or `requires_skills` fields -- those are added by the skill registration process.

## Dependencies

| Dependency | Purpose |
|------------|---------|
| `PyYAML` | Template parsing (transitive via codomyrmex core) |
| `SkillLoader` | Template discovery during skill initialization |
| `SkillsManager` | Custom skill creation using template schemas |

## Constraints

- Template files must be valid YAML parseable by `yaml.safe_load()`.
- The `example` field in patterns and anti-patterns must contain syntactically valid Python code.
- No template may reference external URLs or network resources at load time.
- Templates are versioned with the codomyrmex release (currently v1.1.4).

## Navigation

- Parent: [skills module](../../README.md)
- Related: [skills MCP tools](../../mcp_tools.py)
- Root: [codomyrmex](../../../../../README.md)
