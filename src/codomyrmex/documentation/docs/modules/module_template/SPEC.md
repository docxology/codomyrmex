# Module Template - Technical Specification

**Version**: v1.1.9 | **Last Updated**: March 2026

## Overview

The Module Template defines the canonical structure for new Codomyrmex modules and provides a scaffolding utility to generate complete module skeletons with all required RASP documentation, API/MCP specifications, and Python package boilerplate.

## Design Principles

- **Zero-Mock Policy**: Scaffold tests create real directories and verify real file content.
- **Explicit Failure**: Invalid module names raise `ValueError`; existing directories raise `FileExistsError`.
- **Convention Over Configuration**: All modules follow the same structure; the template enforces consistency.

## Architecture

```
module_template/
  __init__.py                # Package marker (empty __all__)
  scaffold.py                # scaffold_new_module() + helper functions
  README.md                  # Template README
  AGENTS.md                  # Template agent coordination
  SPEC.md                    # Template specification
  PAI.md                     # Template PAI integration
  API_SPECIFICATION.md       # Template API spec
  MCP_TOOL_SPECIFICATION.md  # Template MCP tool spec
  CHANGELOG.md               # Template changelog
  SECURITY.md                # Template security doc
  USAGE_EXAMPLES.md          # Template usage examples
  requirements.template.txt  # Template requirements
  py.typed                   # PEP 561 marker
```

## Functional Requirements

1. Copy all template files to the new module directory.
2. Replace template placeholders with the new module name in all copied files.
3. Validate module names against `^[a-z][a-z0-9_]*$` regex.
4. Generate a core module Python file (`{module_name}.py`) with module docstring and imports.
5. Prevent overwriting existing directories.
6. Support custom target paths for module creation.

## Interface Contracts

```python
def scaffold_new_module(
    module_name: str,
    target_path: Path | None = None,
    description: str = "",
    author: str = "",
) -> Path:
    """
    Create a new Codomyrmex module from the template.

    Raises:
        FileExistsError: If the target directory already exists.
        ValueError: If module_name is invalid (not snake_case).

    Returns:
        Path to the created module directory.
    """

TEMPLATE_FILES: list[str] = [
    "AGENTS.md", "API_SPECIFICATION.md", "CHANGELOG.md",
    "MCP_TOOL_SPECIFICATION.md", "README.md", "SECURITY.md",
    "SPEC.md", "USAGE_EXAMPLES.md", "__init__.py", ".gitignore",
]
```

## Dependencies

**Internal**: `codomyrmex.logging_monitoring`

**External**: `re` (stdlib), `shutil` (stdlib), `pathlib` (stdlib)

## Constraints

- Module names must match `^[a-z][a-z0-9_]*$`.
- Template files must exist in the `module_template/` directory; missing files produce a warning but do not abort.
- The generated `__init__.py` contains the module docstring but no functional exports.

## Navigation

- [readme.md](readme.md) -- Module overview
- [AGENTS.md](AGENTS.md) -- Agent coordination
- [Source Module](../../../../module_template/)
