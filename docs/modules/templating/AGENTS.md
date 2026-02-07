# Templating Module — Agent Coordination

## Purpose

Templating module for Codomyrmex.

## Key Capabilities

- **TemplatingError**: Raised when templating operations fail.
- `get_default_engine()`: Get or create default template engine instance.
- `render()`: Render a template string with context data.
- `render_file()`: Load and render a template file.

## Agent Usage Patterns

```python
from codomyrmex.templating import TemplatingError

# Agent initializes templating
instance = TemplatingError()
```

## Integration Points

- **Source**: [src/codomyrmex/templating/](../../../src/codomyrmex/templating/)
- **Docs**: [Module Documentation](README.md)
- **Spec**: [Technical Specification](SPEC.md)
