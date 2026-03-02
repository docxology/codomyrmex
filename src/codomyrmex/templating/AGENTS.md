# Agent Guidelines - Templating

**Version**: v1.0.5 | **Status**: Active | **Last Updated**: March 2026

## Module Overview

Template engine support (Jinja2, Mako) for code generation and dynamic content.

## Key Classes

- **TemplateEngine** — Configurable template engine
- **Template** — Loaded template object
- **TemplateManager** — Template directory management
- **render()** — Convenience function for rendering
- **render_file()** — Render template from file

## Agent Instructions

1. **Choose engine wisely** — Jinja2 for HTML/configs, Mako for Python-heavy
2. **Use render() for simple** — Convenience function for quick templates
3. **Cache templates** — Use `TemplateEngine` for repeated rendering
4. **Register filters** — Add custom filters for complex transformations
5. **Handle errors** — Catch `TemplatingError` for invalid templates

## Common Patterns

```python
from codomyrmex.templating import render, TemplateEngine

# Simple rendering
output = render("Hello {{ name }}!", {"name": "World"})

# Complex template with engine
engine = TemplateEngine(engine="jinja2")

# Add custom filter
engine.add_filter("uppercase", str.upper)

# Render with data
template = engine.load_template("report.html.j2")
result = template.render({
    "title": "Report",
    "items": data_items
})
```

## Testing Patterns

```python
# Verify template rendering
from codomyrmex.templating import render

output = render("{{ x + y }}", {"x": 1, "y": 2})
assert output == "3"

# Verify file rendering
output = render_file("templates/test.j2", {"name": "test"})
assert "test" in output
```

## PAI Agent Role Access Matrix

| PAI Agent | Access Level | Primary Capabilities | Trust Level |
|-----------|-------------|---------------------|-------------|
| **Engineer** | Full | Direct Python import, class instantiation, full API access | TRUSTED |
| **Architect** | Read + Design | API review, interface design, dependency analysis | OBSERVED |
| **QATester** | Validation | Integration testing via pytest, output validation | OBSERVED |

### Engineer Agent
**Use Cases**: Render Jinja2/Mako templates for code generation and documentation output during BUILD phases

### Architect Agent
**Use Cases**: Design template schemas, define variable contracts, plan template inheritance hierarchies

### QATester Agent
**Use Cases**: Validate template rendering fidelity, verify variable substitution correctness, test error handling for malformed templates

## Navigation

- [README](README.md) | [SPEC](SPEC.md) | [PAI](PAI.md)
