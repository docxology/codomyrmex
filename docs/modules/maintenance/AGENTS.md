# Tools Module — Agent Coordination

## Purpose

Tools Module for Codomyrmex.

## Key Capabilities

- Tools operations and management

## Agent Usage Patterns

```python
from codomyrmex.tools import *

# Agent uses tools capabilities
```

## Integration Points

- **Source**: [src/codomyrmex/tools/](../../../src/codomyrmex/tools/)
- **Docs**: [Module Documentation](README.md)
- **Spec**: [Technical Specification](SPEC.md)


## Key Components

- **`DependencyAnalyzer`** — Analyzes module dependencies for circular imports and hierarchy violations.
- **`get_module_name()`** — Extract module name from file path.
- **`get_dependency_location()`** — Determine where dependencies are located in pyproject.toml.
- **`add_deprecation_notice()`** — Add deprecation notice to requirements.txt file.
- **`main()`** — Main function.
- **`analyze_project_structure()`** — Analyze the overall project structure.

## Testing Guidelines

```bash
uv run python -m pytest src/codomyrmex/tests/ -k tools -v
```

- Run tests before and after making changes.
- Ensure all existing tests pass before submitting.
