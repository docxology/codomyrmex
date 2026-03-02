# Personal AI Infrastructure -- Module Template

**Version**: v1.0.5 | **Status**: Active | **Last Updated**: March 2026

## Overview

The Module Template module provides the canonical scaffolding system for creating
new Codomyrmex modules. It contains `scaffold_new_module()`, which generates a
complete module directory with all required documentation files and a boilerplate
Python source file. Every new module created through this system starts with the
correct RASP documentation pattern, proper `__init__.py` exports, and a typed
class skeleton -- ensuring consistency across the 89+ modules in the monorepo.

## PAI Capabilities

### Programmatic Module Creation

PAI agents can invoke `scaffold_new_module()` to create new modules at runtime:

```python
from codomyrmex.module_template import scaffold_new_module, list_template_files

# Create a new module
result_path = scaffold_new_module(
    module_name="my_new_feature",
    description="Handles feature X for the platform",
    author="PAI"
)
# result_path => src/codomyrmex/my_new_feature/

# List available template files
files = list_template_files()
# => ['AGENTS.md', 'API_SPECIFICATION.md', 'CHANGELOG.md', ...]
```

### Template File Inventory

The scaffolding copies and customizes these files into every new module:

| Template File | Purpose |
|--------------|---------|
| `README.md` | Module overview, key exports, quick start |
| `AGENTS.md` | Agent coordination documentation |
| `SPEC.md` | Functional specification |
| `API_SPECIFICATION.md` | Programmatic API surface |
| `MCP_TOOL_SPECIFICATION.md` | MCP tool definitions (if module exposes `@mcp_tool`) |
| `CHANGELOG.md` | Version history |
| `SECURITY.md` | Security considerations |
| `USAGE_EXAMPLES.md` | Runnable usage examples |
| `__init__.py` | Package marker with docstring |

Additionally, `_create_core_module()` generates a `{module_name}.py` file containing:

- A typed class with `__init__` and `process()` methods
- A convenience factory function `create_{module_name}()`
- Proper logging via `get_logger(__name__)`
- `NotImplementedError` for unimplemented methods (per zero-mock policy)

### RASP Documentation Pattern

Every Codomyrmex module follows the RASP documentation convention:

| Document | Content |
|----------|---------|
| **R** -- `README.md` | Human-readable overview, exports table, quick-start code |
| **A** -- `AGENTS.md` | How agents coordinate around this module |
| **S** -- `SPEC.md` | Functional specification and design principles |
| **P** -- `PAI.md` | PAI integration: phase mapping, MCP tools, capabilities |

When PAI creates a new module, all four RASP documents are generated automatically.
The PAI.md file starts as a stub and should be expanded with phase-specific
details once the module's capabilities are implemented.

### Module Name Validation

`scaffold_new_module()` enforces snake_case naming via the regex `^[a-z][a-z0-9_]*$`.
Invalid names raise `ValueError`. This ensures:

- Consistent import paths (`from codomyrmex.my_module import ...`)
- Valid Python package names
- Predictable directory structure

## PAI Algorithm Phase Mapping

| Phase | Module Template Contribution | How |
|-------|-----------------------------|-----|
| **OBSERVE** | Template discovery | `list_template_files()` reveals what documentation and code a new module will receive |
| **THINK** | Module design assessment | PAI evaluates whether a new module is needed vs extending an existing one |
| **PLAN** | Scaffolding plan | PAI plans the module name, description, and where it fits in the layer hierarchy |
| **BUILD** | Module creation | `scaffold_new_module()` creates the directory, documentation, and boilerplate code |
| **EXECUTE** | Template customization | Replacements (module name, description, author) are applied to all template files |
| **VERIFY** | Structural validation | After scaffolding, PAI can verify the new module has all RASP files and a valid `__init__.py` |
| **LEARN** | Pattern reinforcement | Each successful scaffolding run reinforces the canonical module structure in PAI's context |

## Scaffolding Internals

### Text Replacement System

`_copy_and_customize()` performs three replacement passes on every template file:

| Placeholder | Replaced With | Example |
|------------|--------------|---------|
| `module_template` | `module_name` (snake_case) | `my_feature` |
| `Module Template` | Title-cased module name | `My Feature` |
| `MODULE_TEMPLATE` | Uppercase module name | `MY_FEATURE` |

For `README.md`, the description is inserted after the first `#` heading.

### Generated Core Module Structure

The boilerplate Python file follows this pattern:

```python
class MyFeature:
    def __init__(self, config=None):
        self.config = config or {}

    def process(self, data):
        raise NotImplementedError(
            "scaffold.process() requires implementation by consuming module"
        )

def create_my_feature(config=None):
    return MyFeature(config)
```

This ensures every new module starts with a typed, logged, testable skeleton.

## Architecture Role

**Specialized Layer** -- The module template lives in the Specialized layer.
It imports only from Foundation (`logging_monitoring`) and uses stdlib only
(`re`, `shutil`, `pathlib`).

```
module_template/
  __init__.py              # Package marker
  scaffold.py              # scaffold_new_module(), list_template_files()
  requirements.template.txt
  AGENTS.md                # Template docs (copied into new modules)
  API_SPECIFICATION.md
  CHANGELOG.md
  MCP_TOOL_SPECIFICATION.md
  README.md
  SECURITY.md
  SPEC.md
  USAGE_EXAMPLES.md
```

## Relationship to Other Modules

| Module | Relationship |
|--------|-------------|
| `logging_monitoring` | Scaffold uses `get_logger` for structured logging during creation |
| `documentation` | Generated RASP docs follow the documentation module's standards |
| All modules | Every module in the monorepo was (or could be) created from this template |

## MCP Tools

This module does not expose MCP tools directly. Access its capabilities via:
- Direct Python import: `from codomyrmex.module_template import ...`
- CLI: `codomyrmex module_template <command>`

## Navigation

- **Self**: [PAI.md](PAI.md)
- **Parent**: [../PAI.md](../PAI.md) -- Source-level PAI module map
- **Root Bridge**: [../../../PAI.md](../../../PAI.md) -- Authoritative PAI system bridge doc
- **Siblings**: [README.md](README.md) | [AGENTS.md](AGENTS.md) | [SPEC.md](SPEC.md) | [API_SPECIFICATION.md](API_SPECIFICATION.md)
