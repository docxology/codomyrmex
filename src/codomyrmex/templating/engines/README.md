# Engines

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

Template engine implementations for the templating module. Provides three template rendering engines -- simple variable interpolation, a Jinja2-like engine with control structures and filters, and a Mustache-style logic-less engine -- all sharing a common abstract interface.

## Key Exports

### Context

- **`TemplateContext`** -- Hierarchical context with parent chain lookup, child context creation, and dict-like access

### Engine Base

- **`TemplateEngine`** -- Abstract base class defining `render(template, context)` and `render_file(path, context)` interface

### Engine Implementations

- **`SimpleTemplateEngine`** -- String interpolation engine using configurable delimiters (default `{{ }}`); supports dotted path resolution and optional HTML escaping
- **`Jinja2LikeEngine`** -- Full-featured engine with:
  - Variable interpolation with dotted/subscript paths
  - For loops (`{% for item in items %}`) with `loop` variable (index, first, last, length)
  - If/else blocks (`{% if condition %}`) with comparison, boolean, and membership operators
  - Filter pipeline (`{{ value | upper | default("N/A") }}`) with 12 built-in filters (upper, lower, title, strip, length, default, safe, escape, join, first, last, reverse, sort)
  - Auto-escaping with opt-out via `safe` filter
- **`MustacheEngine`** -- Logic-less Mustache templates with:
  - Variable interpolation with HTML escaping (triple mustache `{{{ }}}` or `&` for unescaped)
  - Truthy sections (`{{#section}}`) with list iteration and context pushing
  - Inverted sections (`{{^section}}`) for falsy values
  - Dotted path resolution

### Factory

- **`create_engine()`** -- Factory function to create engines by type string ("simple", "jinja2", "mustache")

## Directory Contents

- `__init__.py` - All engine classes and factory (487 lines)
- `template_engine.py` - Additional template engine utilities
- `py.typed` - PEP 561 type stub marker

## Usage

```python
from codomyrmex.templating.engines import create_engine

# Simple interpolation
simple = create_engine("simple")
output = simple.render("Hello {{ user.name }}!", {"user": {"name": "World"}})

# Jinja2-like with filters and loops
jinja = create_engine("jinja2")
output = jinja.render("""
{% for item in items %}
  {{ loop.index }}. {{ item.name | upper }}
{% endfor %}
""", {"items": [{"name": "alpha"}, {"name": "beta"}]})

# Mustache logic-less
mustache = create_engine("mustache")
output = mustache.render("{{#users}}Hi {{name}}! {{/users}}", {"users": [{"name": "Alice"}]})
```

## Navigation

- **Parent Module**: [templating](../README.md)
- **Project Root**: [../../../../README.md](../../../../README.md)
