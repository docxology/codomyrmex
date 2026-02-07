# Module Template Module — Agent Coordination

## Purpose

Module Template Package

## Key Capabilities

- Module Template operations and management

## Agent Usage Patterns

```python
from codomyrmex.module_template import *

# Agent uses module template capabilities
```

## Integration Points

- **Source**: [src/codomyrmex/module_template/](../../../src/codomyrmex/module_template/)
- **Docs**: [Module Documentation](README.md)
- **Spec**: [Technical Specification](SPEC.md)


## Key Components

- **`scaffold_new_module()`** — Create a new Codomyrmex module from the template.
- **`list_template_files()`** — List all files available in the module template.

## Testing Guidelines

```bash
uv run python -m pytest src/codomyrmex/tests/ -k module_template -v
```

- Run tests before and after making changes.
- Ensure all existing tests pass before submitting.
