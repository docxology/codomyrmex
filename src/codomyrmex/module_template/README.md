# Module Template Module

**Version**: v0.1.7 | **Status**: Active | **Last Updated**: February 2026

## Overview

Scaffolding module for creating new Codomyrmex modules from a standardized template. The `scaffold_new_module()` function generates a complete module directory with all required documentation files (README, AGENTS, SPEC, API_SPECIFICATION, CHANGELOG, MCP_TOOL_SPECIFICATION, SECURITY, USAGE_EXAMPLES), a customized `__init__.py`, and a core Python source file with a boilerplate class and factory function. Module names are validated to enforce snake_case naming conventions.


## Installation

```bash
uv add codomyrmex
```

Or for development:

```bash
uv sync
```

## Key Exports

### Functions

- **`scaffold_new_module()`** -- Create a new Codomyrmex module directory from the template, copying and customizing all standard files. Accepts module_name, target_path, description, and author. Raises FileExistsError if target exists, ValueError for invalid names.
- **`list_template_files()`** -- List all files available in the module template directory

### Internal Helpers

- **`_copy_and_customize()`** -- Copy a template file to the target, performing text replacements for module name and description
- **`_create_core_module()`** -- Generate the main Python source file with a boilerplate class and factory function

## Directory Contents

- `__init__.py` - Package marker with module docstring
- `scaffold.py` - Core scaffolding logic: `scaffold_new_module()`, `list_template_files()`, and template file helpers
- `requirements.template.txt` - Template requirements file copied into new modules
- `AGENTS.md` - Template AGENTS documentation
- `API_SPECIFICATION.md` - Template API specification
- `CHANGELOG.md` - Template changelog
- `MCP_TOOL_SPECIFICATION.md` - Template MCP tool specification
- `SECURITY.md` - Template security documentation
- `SPEC.md` - Template module specification
- `USAGE_EXAMPLES.md` - Template usage examples

## Quick Start

```python
from codomyrmex.module_template import scaffold_new_module, list_template_files

result = scaffold_new_module()
```


## Testing

```bash
uv run python -m pytest src/codomyrmex/tests/ -k module_template -v
```

## Navigation

- **Full Documentation**: [docs/modules/module_template/](../../../docs/modules/module_template/)
- **Parent Directory**: [codomyrmex](../README.md)
- **Project Root**: ../../../README.md
