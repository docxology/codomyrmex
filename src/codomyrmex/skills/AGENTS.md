# Agent Guidelines - Skills

**Version**: v1.0.5 | **Status**: Active | **Last Updated**: March 2026

## Module Overview

Agent skill management: discovery, registration, and execution.

## Key Classes

- **Skill** — Base skill class
- **SkillRegistry** — Discover and register skills
- **SkillExecutor** — Execute skills
- **SkillComposer** — Compose skills

## MCP Tools Available

All tools are auto-discovered via `@mcp_tool` decorators and exposed through the MCP bridge.

| Tool | Description | Trust Level |
|------|-------------|-------------|
| `skills_list` | List available skills, optionally filtered by category | Safe |
| `skills_get` | Get a specific skill by category and name | Safe |
| `skills_search` | Search skills by query string | Safe |
| `skills_sync` | Sync with upstream vibeship-spawner-skills repository | Safe |
| `skills_add_custom` | Add a custom skill that overrides upstream | Safe |
| `skills_get_categories` | Get all available skill categories | Safe |
| `skills_get_upstream_status` | Get status of upstream repository (exists, branch, last commit) | Safe |

## Agent Instructions

1. **Register skills** — Add to registry on startup
2. **Version skills** — Track skill versions
3. **Dependencies** — Declare skill dependencies
4. **Input validation** — Validate skill inputs
5. **Document skills** — Clear descriptions

## Common Patterns

```python
from codomyrmex.skills import Skill, SkillRegistry, SkillExecutor

# Define a skill
@Skill(name="code_review", version="1.0")
def review_code(code: str, language: str = "python"):
    \"\"\"Review code for issues.\"\"\"
    return analyze(code, language)

# Register skills
registry = SkillRegistry()
registry.register(review_code)
registry.discover("./skills/")  # Auto-discover

# List available skills
for skill in registry.list():
    print(f"{skill.name} v{skill.version}: {skill.description}")

# Execute skills
executor = SkillExecutor(registry)
result = executor.execute("code_review", code=source, language="python")

# Compose skills
composed = registry.compose(["parse", "analyze", "format"])
result = executor.execute_composed(composed, input_data)
```

## Testing Patterns

```python
# Verify skill registration
registry = SkillRegistry()
registry.register(review_code)
assert "code_review" in registry.list_names()

# Verify execution
executor = SkillExecutor(registry)
result = executor.execute("code_review", code="print(1)")
assert result is not None
```

## PAI Agent Role Access Matrix

| PAI Agent | Access Level | Primary Capabilities | Trust Level |
|-----------|-------------|---------------------|-------------|
| **Engineer** | Full | All 7 `skills_*` tools; skill discovery, invocation, and lifecycle management | TRUSTED |
| **Architect** | Read + Design | `skills_list`, `skills_get`; skill inventory review, skill architecture design | OBSERVED |
| **QATester** | Validation | `skills_list`, `skills_get`; skill availability verification, invocation testing | OBSERVED |

### Engineer Agent
**Use Cases**: Discovering and invoking skills during EXECUTE, managing skill lifecycle, building skill composition workflows.

### Architect Agent
**Use Cases**: Reviewing installed skill catalog, designing skill composition patterns, planning skill architecture.

### QATester Agent
**Use Cases**: Verifying skill discovery during VERIFY, confirming skill invocation correctness.

## Navigation

- [README](README.md) | [SPEC](SPEC.md) | [PAI](PAI.md)
