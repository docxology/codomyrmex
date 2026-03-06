# Agent Guidelines - Templating

**Version**: v1.1.4 | **Status**: Active | **Last Updated**: March 2026

## Module Overview

Template engine support for code generation and dynamic content using Jinja2 and Mako. Provides
`TemplateEngine` for configurable multi-engine rendering, `TemplateManager` for directory-based
template discovery, and the `render()` convenience function for one-off string rendering. Two MCP
tools (`template_render`, `template_validate`) expose template operations to PAI agents without
requiring Python imports.

## Key Files

| File | Purpose |
|------|---------|
| `__init__.py` | Exports `TemplateEngine`, `Template`, `TemplateManager`, `render`, `render_file` |
| `engines/template_engine.py` | `TemplateEngine` — configurable Jinja2/Mako engine with filter registration |
| `template_manager.py` | `TemplateManager` — directory scanning and template lifecycle |
| `mcp_tools.py` | MCP tools: `template_render`, `template_validate` |

## Key Classes

- **TemplateEngine** — Configurable template engine (Jinja2 or Mako)
- **Template** — Loaded template object with `render()` method
- **TemplateManager** — Template directory management and discovery
- **`render()`** — Convenience function for quick one-off string rendering
- **`render_file()`** — Render a template from a file path

## MCP Tools Available

| Tool | Description | Trust Level |
|------|-------------|-------------|
| `template_render` | Render a Jinja2 template string with provided context variables | SAFE |
| `template_validate` | Validate a Jinja2 template string for syntax errors | SAFE |

## Agent Instructions

1. **Choose engine wisely** — Jinja2 for HTML/configs; Mako for Python-heavy templates
2. **Use `render()` for simple** — Convenience function for quick one-off rendering
3. **Cache templates** — Use `TemplateEngine` for repeated rendering of the same template
4. **Register filters** — Add custom filters for complex transformations before first use
5. **Handle errors** — Catch `TemplatingError` for invalid template syntax

## Operating Contracts

- `TemplateEngine` instances are not thread-safe — create one per concurrent task
- `render()` uses Jinja2 by default; specify `engine=` to change
- `template_render` MCP tool escapes HTML by default — use `| safe` filter to opt out
- `TemplateManager.load()` returns a `Template` object — call `.render(context)` to produce output
- **DO NOT** use `Jinja2Template(template, environment=env)` — use `env.from_string(template)`

## Common Patterns

```python
from codomyrmex.templating import render, TemplateEngine

# Simple one-off rendering
output = render("Hello {{ name }}!", {"name": "World"})

# Reusable engine with custom filter
engine = TemplateEngine(engine="jinja2")
engine.add_filter("uppercase", str.upper)

template = engine.load_template("report.html.j2")
result = template.render({
    "title": "Report",
    "items": data_items
})
```

## Testing Patterns

```python
from codomyrmex.templating import render

# Verify expression rendering
output = render("{{ x + y }}", {"x": 1, "y": 2})
assert output == "3"

# Verify filter application
output = render("{{ name | upper }}", {"name": "world"})
assert output == "WORLD"
```

## PAI Agent Role Access Matrix

| PAI Agent | Access Level | MCP Tools | Trust Level |
|-----------|-------------|-----------|-------------|
| **Engineer** | Full | `template_render`, `template_validate` | TRUSTED |
| **Architect** | Read + Design | `template_validate` — template schema design and syntax review | OBSERVED |
| **QATester** | Validation | `template_render`, `template_validate` — rendering fidelity verification | OBSERVED |
| **Researcher** | Read-only | `template_render`, `template_validate` — template inspection and syntax validation | SAFE |

### Engineer Agent
**Use Cases**: Render Jinja2/Mako templates for code generation and documentation output during BUILD phases.

### Architect Agent
**Use Cases**: Design template schemas, define variable contracts, plan template inheritance hierarchies.

### QATester Agent
**Use Cases**: Validate template rendering fidelity, verify variable substitution, test error handling for malformed templates.

### Researcher Agent
**Use Cases**: Rendering and validating template syntax during research analysis of code generation pipelines.

## Navigation

- [README](README.md) | [SPEC](SPEC.md) | [PAI](PAI.md)
