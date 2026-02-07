# Tests Module — Agent Coordination

## Purpose

Codomyrmex Tests Package

## Key Capabilities

- Tests operations and management

## Agent Usage Patterns

```python
from codomyrmex.tests import *

# Agent uses tests capabilities
```

## Integration Points

- **Source**: [src/codomyrmex/tests/](../../../src/codomyrmex/tests/)
- **Docs**: [Module Documentation](README.md)
- **Spec**: [Technical Specification](SPEC.md)

## Key Components

- **`pytest_configure()`** — Register custom pytest markers.
- **`project_root()`** — Fixture providing the project root path.
- **`code_dir()`** — Fixture providing the code directory path.
- **`temp_env_file()`** — Fixture providing a temporary .env file path.
- **`sample_markdown_file()`** — Fixture providing a sample markdown file.

### Submodules

- `examples` — Examples

