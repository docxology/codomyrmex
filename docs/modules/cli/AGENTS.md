# CLI Module — Agent Coordination

## Purpose

This module provides the command-line interface for the Codomyrmex development platform.

## Key Capabilities

- CLI operations and management

## Agent Usage Patterns

```python
from codomyrmex.cli import *

# Agent uses cli capabilities
```

## Integration Points

- **Source**: [src/codomyrmex/cli/](../../../src/codomyrmex/cli/)
- **Docs**: [Module Documentation](README.md)
- **Spec**: [Technical Specification](SPEC.md)


## Key Components

- **`main()`** — Enhanced main CLI entry point with comprehensive functionality.
- **`get_formatter()`** — Get TerminalFormatter if available.
- **`print_success()`** — print_success
- **`print_error()`** — print_error
- **`print_warning()`** — print_warning

### Submodules

- `completions` — Completions
- `formatters` — Formatters
- `handlers` — Handlers
- `parsers` — Parsers
- `themes` — Themes

## Testing Guidelines

```bash
uv run python -m pytest src/codomyrmex/tests/ -k cli -v
```

- Run tests before and after making changes.
- Ensure all existing tests pass before submitting.
