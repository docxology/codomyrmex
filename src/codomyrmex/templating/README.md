# Templating Module

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Overview

The Templating module provides template engine support for Codomyrmex, enabling code generation, documentation templates, and dynamic content rendering.

## Supported Engines

| Engine | Description |
|--------|-------------|
| `jinja2` | Full-featured, most popular Python template engine (default) |
| `mako` | Fast, flexible, Pythonic template language |

## Key Features

- **Multi-Engine Support**: Jinja2 and Mako engines
- **Template Management**: Organize and load templates
- **Context Rendering**: Pass variables to templates
- **Inheritance**: Template inheritance and includes
- **Filters & Macros**: Jinja2 filters and macro support

## Quick Start

```python
from codomyrmex.templating import (
    render, get_template_engine,
    Template, TemplateEngine, TemplateManager,
)

# Simple template rendering
template_str = "Hello, {{ name }}! You have {{ count }} messages."
output = render(template_str, {"name": "Alice", "count": 5})
# Output: "Hello, Alice! You have 5 messages."

# Using the TemplateEngine class
engine = get_template_engine(engine="jinja2")

# Render with loops and conditionals
template = '''
{% for item in items %}
- {{ item.name }}: ${{ item.price }}
{% endfor %}
Total: {{ items | length }} items
'''
output = engine.render(template, {"items": [
    {"name": "Widget", "price": 9.99},
    {"name": "Gadget", "price": 19.99},
]})

# Template Manager for file-based templates
manager = TemplateManager(template_dir="templates/")
template = manager.get("email/welcome.html")
output = template.render({"user": user_data})
```

## Core Classes

| Class | Description |
|-------|-------------|
| `TemplateEngine` | Core template rendering with engine selection |
| `TemplateManager` | Manage template files and directories |
| `Template` | Individual template with render method |

## Convenience Functions

| Function | Description |
|----------|-------------|
| `render(template, context, engine)` | Render a template string |
| `get_template_engine(engine)` | Get a TemplateEngine instance |

## Exceptions

| Exception | Description |
|-----------|-------------|
| `TemplatingError` | Template rendering failed |

## Navigation

- **Technical Documentation**: [AGENTS.md](AGENTS.md)
- **Functional Specification**: [SPEC.md](SPEC.md)
- **Parent Directory**: [codomyrmex](../README.md)
- **Project Root**: [README](../../../README.md)
