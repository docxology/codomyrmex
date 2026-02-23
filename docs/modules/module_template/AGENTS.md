# Agent Guidelines - Module Template

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

## Module Overview

Template for creating new Codomyrmex modules.

## Template Structure

```
module_name/
├── README.md           # Module documentation
├── AGENTS.md           # Agent guidelines
├── SPEC.md             # Functional specification
├── PAI.md              # Personal AI Infrastructure  
├── API_SPECIFICATION.md
├── __init__.py         # Module exports
├── core.py             # Core functionality
└── tests/              # Module tests
```

## Agent Instructions

1. **Copy template** — Start from this template
2. **Update all docs** — README, AGENTS, SPEC, PAI
3. **Define exports** — Clean `__init__.py` exports
4. **Add tests** — Minimum 80% coverage
5. **Follow patterns** — Consistent with other modules

## Common Patterns

```python
# __init__.py structure
\"\"\"Module description.

This module provides...
\"\"\"

from .core import MainClass, helper_function
from .types import CustomType

__all__ = [
    "MainClass",
    "helper_function",
    "CustomType",
]

__version__ = "0.1.0"
```

## Creating a Module

```bash
# Copy template
cp -r src/codomyrmex/module_template src/codomyrmex/new_module

# Update placeholders
# - module_name in all files
# - Update descriptions
# - Implement core.py
# - Add tests
```

## Testing Patterns

```python
# Verify module structure
import new_module
assert hasattr(new_module, "__version__")
assert hasattr(new_module, "__all__")
```

## Navigation

- [README](README.md) | [SPEC](SPEC.md) | [PAI](PAI.md)
