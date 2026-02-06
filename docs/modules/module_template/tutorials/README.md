# Module Template Tutorials

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

Tutorials for creating new Codomyrmex modules using the template.

## Available Tutorials

| Tutorial | Description |
|----------|-------------|
| [Create Module](#create-module) | Create a new module from template |
| [Structure](#structure) | Understand module structure |
| [Documentation](#documentation) | Document your module |

## Create Module

```bash
# Copy template
cp -r src/codomyrmex/module_template src/codomyrmex/my_module

# Update module name in files
sed -i '' 's/module_template/my_module/g' src/codomyrmex/my_module/*.md
```

## Structure

```
my_module/
├── README.md           # Human documentation
├── AGENTS.md           # AI agent guidelines
├── SPEC.md             # Functional specification
├── PAI.md              # Personal AI Infrastructure
├── __init__.py         # Module exports
├── core.py             # Core implementation
└── tests/              # Module tests
```

## Documentation

Every module should have:

1. **README.md** — Quick start and examples
2. **AGENTS.md** — AI agent instructions
3. **SPEC.md** — Technical specification
4. **PAI.md** — PAI integration

## Navigation

- **Parent**: [Module Template Documentation](../README.md)
- **Source**: [src/codomyrmex/module_template/](../../../../src/codomyrmex/module_template/)
