# Discovery

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

Skill discovery and registration utilities. Provides a complete framework for defining, registering, searching, and auto-discovering agent skills with metadata, parameter schemas, and JSON Schema export for LLM tool calling.

## Key Exports

### Enums

- **`SkillCategory`** -- Skill categories: CODE, DATA, WEB, FILE, SYSTEM, COMMUNICATION, REASONING, UTILITY

### Schema and Metadata

- **`ParameterSchema`** -- Schema for a skill parameter with name, type, description, required flag, default, and enum values
- **`SkillMetadata`** -- Full skill metadata including id, name, description, version, category, tags, parameters, examples, and JSON Schema export for LLM tool calling

### Skill Base Classes

- **`Skill`** -- Abstract base class with `execute()` and `validate_params()` methods
- **`FunctionSkill`** -- Wraps any callable into a Skill, auto-inferring metadata from function signature, type hints, and docstring

### Registry and Discovery

- **`SkillRegistry`** -- Central registry supporting register, unregister, search (by query, category, tags), list, and execute operations with category and tag indexing
- **`SkillDiscoverer`** -- Discovers skills from Python modules by scanning for Skill instances and subclasses
- **`DEFAULT_REGISTRY`** -- Module-level global SkillRegistry instance

### Convenience Functions

- **`skill()`** -- Decorator to create a FunctionSkill from a function with optional name, description, category, tags, and auto-registration
- **`register_skill()`** -- Register a skill in the default global registry
- **`get_skill()`** -- Retrieve a skill from the default global registry by ID

## Directory Contents

- `__init__.py` - All discovery classes, registry, and decorator (399 lines)
- `py.typed` - PEP 561 type stub marker

## Usage

```python
from codomyrmex.skills.discovery import skill, SkillCategory, DEFAULT_REGISTRY

@skill(name="summarize", category=SkillCategory.REASONING, registry=DEFAULT_REGISTRY)
def summarize_text(text: str, max_length: int = 100) -> str:
    """Summarize input text."""
    return text[:max_length]

# Search by category
results = DEFAULT_REGISTRY.search(category=SkillCategory.REASONING)

# Export for LLM tool calling
schema = results[0].metadata.to_json_schema()
```

## Navigation

- **Parent Module**: [skills](../README.md)
- **Project Root**: [../../../../README.md](../../../../README.md)
