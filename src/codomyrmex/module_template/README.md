# module_template

## Signposting
- **Parent**: [codomyrmex](../README.md)
- **Children**:
    - [docs](docs/README.md)
    - [tests](tests/README.md)
- **Key Artifacts**:
    - [Agent Guide](AGENTS.md)
    - [Functional Spec](SPEC.md)

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Overview

Scaffolding and generation logic for creating new Codomyrmex modules. Ensures all new modules start with required structure, documentation files (README, AGENTS, SPEC), and configuration, enforcing Internal Coherence design principle. Uses template-driven approach with Jinja2 for generating files from templates. Supports idempotent module creation and upgrading existing folders to modules.

## Directory Contents
- `API_SPECIFICATION.md` – File
- `CHANGELOG.md` – File
- `MCP_TOOL_SPECIFICATION.md` – File
- `README.md` – File
- `SECURITY.md` – File
- `SPEC.md` – File
- `USAGE_EXAMPLES.md` – File
- `__init__.py` – File
- `docs/` – Subdirectory
- `requirements.template.txt` – File
- `tests/` – Subdirectory

## Navigation
- **Technical Documentation**: [AGENTS.md](AGENTS.md)
- **Functional Specification**: [SPEC.md](SPEC.md)
- **Parent Directory**: [codomyrmex](../README.md)
- **Project Root**: [README](../../../README.md)

## Getting Started

This module is used internally by Codomyrmex to generate new modules. To create a new module:

```python
# This module provides scaffolding tools for creating new Codomyrmex modules
# Typically used via CLI or internal tooling

# Example: Generate a new module structure
# (This would typically be done via a CLI command or script)
# The module_template ensures all new modules have:
# - Proper directory structure
# - Required documentation files (README.md, AGENTS.md, SPEC.md)
# - Standard __init__.py with proper exports
# - Test directory structure
# - Documentation templates
```

