# Module Template - Agent Coordination

**Version**: v1.1.0 | **Last Updated**: March 2026

## Overview

The Module Template provides a standardized starting point for new Codomyrmex modules. Agents use it when scaffolding new modules to ensure all required documentation, configuration, and code structure is in place from the start.

## Key Files

| File | Class/Function | Role |
|------|---------------|------|
| `scaffold.py` | `scaffold_new_module()` | Create a new module from the template with name/description customization |
| `scaffold.py` | `TEMPLATE_FILES` | List of files copied for each new module |
| `__init__.py` | (package marker) | Makes directory a Python package |
| `README.md` | (template) | README template for new modules |
| `AGENTS.md` | (template) | Agent coordination template |
| `SPEC.md` | (template) | Technical specification template |
| `PAI.md` | (template) | PAI integration template |
| `API_SPECIFICATION.md` | (template) | API specification template |
| `MCP_TOOL_SPECIFICATION.md` | (template) | MCP tool specification template |

## MCP Tools Available

No MCP tools defined for this module.

## Agent Instructions

1. Use `scaffold_new_module(module_name, description, author)` to generate a complete new module.
2. Module names must be snake_case (lowercase letters, numbers, underscores, starting with a letter).
3. The scaffolder raises `FileExistsError` if the target directory already exists.
4. After scaffolding, customize the generated files with module-specific content.
5. Template placeholders (`module_template`, `Module Template`, `MODULE_TEMPLATE`) are automatically replaced with the new module name.

## Operating Contracts

- `scaffold_new_module` validates the module name with regex `^[a-z][a-z0-9_]*$`.
- If `target_path` is None, the module is created at `src/codomyrmex/{module_name}/`.
- A core module file `{module_name}.py` is auto-generated alongside the template files.
- The function returns the `Path` to the created module directory.

## Common Patterns

```python
from codomyrmex.module_template.scaffold import scaffold_new_module

# Scaffold with defaults
path = scaffold_new_module("data_pipeline")

# Scaffold with full options
path = scaffold_new_module(
    module_name="data_pipeline",
    target_path=Path("/custom/location"),
    description="Data pipeline processing module",
    author="Team Name",
)
```

## PAI Agent Role Access Matrix

| Agent | Access Level | Primary Tools |
|-------|-------------|---------------|
| Architect | Full | `scaffold_new_module` |
| Engineer | Full | `scaffold_new_module` |
| QATester | None | No relevant tools |

## Navigation

- [readme.md](readme.md) -- Module overview
- [SPEC.md](SPEC.md) -- Technical specification
- [Source Module](../../../../module_template/)
