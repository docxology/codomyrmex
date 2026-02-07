# Documentation Module — Agent Coordination

## Purpose

Documentation Module for Codomyrmex.

## Key Capabilities

- Documentation operations and management

## Agent Usage Patterns

```python
from codomyrmex.documentation import *

# Agent uses documentation capabilities
```

## Integration Points

- **Source**: [src/codomyrmex/documentation/](../../../src/codomyrmex/documentation/)
- **Docs**: [Module Documentation](README.md)
- **Spec**: [Technical Specification](SPEC.md)


## Key Components

- **`ConsistencyIssue`** — Represents a documentation consistency issue.
- **`ConsistencyReport`** — Report of consistency check results.
- **`DocumentationConsistencyChecker`** — Checks documentation for consistency issues.
- **`DocumentationQualityAnalyzer`** — Analyzes documentation quality metrics.
- **`check_documentation_consistency()`** — Check documentation consistency.
- **`command_exists()`** — Check if a command exists on PATH.
- **`check_doc_environment()`** — Checks for Node.js and npm/yarn.
- **`run_command_stream_output()`** — Helper to run a shell command and stream its output to the logger.
- **`install_dependencies()`** — Installs Docusaurus dependencies.

### Submodules

- `scripts` — Scripts

## Testing Guidelines

```bash
uv run python -m pytest src/codomyrmex/tests/ -k documentation -v
```

- Run tests before and after making changes.
- Ensure all existing tests pass before submitting.
