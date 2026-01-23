# Module Template

**Version**: v0.1.0 | **Status**: Template | **Last Updated**: January 2026

## Overview

This module provides a template for creating new Codomyrmex modules. Copy this directory when creating a new module to ensure consistent structure across the codebase.

## Template Structure

```
module_template/
├── __init__.py           # Module initialization
├── README.md             # This documentation
├── AGENTS.md             # Agent integration guide
├── SPEC.md               # Technical specification
├── PAI.md                # Personal AI context
├── core.py               # Core functionality (rename as needed)
├── exceptions.py         # Module-specific exceptions
└── tests/
    └── test_core.py      # Unit tests
```

## Usage

### Create New Module

```bash
# Copy template
cp -r src/codomyrmex/module_template src/codomyrmex/my_new_module

# Rename and customize
cd src/codomyrmex/my_new_module
# Edit __init__.py, core.py, README.md, etc.
```

### Checklist for New Modules

1. [ ] Rename `module_template` to your module name
2. [ ] Update `__init__.py` with your exports
3. [ ] Update `README.md` with accurate content
4. [ ] Update `AGENTS.md` with agent guidance
5. [ ] Update `SPEC.md` with technical specs
6. [ ] Update `PAI.md` with AI context
7. [ ] Implement core functionality
8. [ ] Add exception classes
9. [ ] Write unit tests
10. [ ] Register in parent `__init__.py`

## Documentation Standards

Each module must include:

- **README.md**: Overview, architecture, quick start
- **AGENTS.md**: Agent operating rules
- **SPEC.md**: Technical specification
- **PAI.md**: Personal AI integration context

## Navigation

- **Parent**: [../README.md](../README.md)
- **Standards**: [AGENTS.md](../../../AGENTS.md)
