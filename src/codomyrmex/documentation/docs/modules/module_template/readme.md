# Module Template

**Version**: v1.0.8 | **Status**: Active | **Last Updated**: March 2026

## Overview

The Module Template provides a standardized template and scaffolding utility for creating new Codomyrmex modules. It includes all required RASP documentation files (README.md, AGENTS.md, SPEC.md, PAI.md), API and MCP specification templates, a changelog template, and a programmatic scaffolding function that generates a complete module structure from the template.

## PAI Integration

| Algorithm Phase | Module Template Role |
|----------------|---------------------|
| BUILD | Scaffold new modules with `scaffold_new_module()` |
| PLAN | Reference template structure when designing new modules |

## Key Exports

The module_template package does not export any classes or functions via `__init__.py`. The scaffolding utility is accessed directly from `scaffold.py`.

## Quick Start

```python
from codomyrmex.module_template.scaffold import scaffold_new_module

# Create a new module from the template
module_path = scaffold_new_module(
    module_name="my_new_module",
    description="A new module for doing interesting things",
    author="Developer Name",
)
# Creates: src/codomyrmex/my_new_module/ with all RASP docs and __init__.py
```

## Architecture

```
module_template/
  __init__.py                # Package marker (no public exports)
  scaffold.py                # scaffold_new_module(), template file copying/customization
  README.md                  # Template README for new modules
  AGENTS.md                  # Template agent coordination doc
  SPEC.md                    # Template technical specification
  PAI.md                     # Template PAI integration doc
  API_SPECIFICATION.md       # Template API specification
  MCP_TOOL_SPECIFICATION.md  # Template MCP tool specification
  CHANGELOG.md               # Template changelog
  SECURITY.md                # Template security documentation
  USAGE_EXAMPLES.md          # Template usage examples
  requirements.template.txt  # Template requirements file
  py.typed                   # PEP 561 marker for type checking
```

## Testing

```bash
uv run pytest src/codomyrmex/tests/unit/module_template/ -v
```

## Navigation

- [AGENTS.md](AGENTS.md) -- Agent coordination documentation
- [SPEC.md](SPEC.md) -- Technical specification
- [Source Module](../../../../module_template/)
