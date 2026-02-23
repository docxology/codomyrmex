# Agent Guidelines - Skills

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

## Module Overview

Agent skill management: discovery, registration, and execution.

## Key Classes

- **Skill** — Base skill class
- **SkillRegistry** — Discover and register skills
- **SkillExecutor** — Execute skills
- **SkillComposer** — Compose skills

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

## Navigation

- [README](README.md) | [SPEC](SPEC.md) | [PAI](PAI.md)
