# Codomyrmex Agents -- templating/engines

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose

Template rendering engine implementations supporting multiple template syntaxes: simple string interpolation, Jinja2-like control structures, and Mustache logic-less templates.

## Key Components

| Component | Role |
|-----------|------|
| `TemplateContext` | Hierarchical context with parent chain lookup via `get()` and `child()` |
| `TemplateEngine` (ABC) | Abstract base defining `render(template, context)` and `render_file(path, context)` |
| `SimpleTemplateEngine` | Regex-based `{{ var }}` interpolation with dotted path resolution and optional HTML escaping |
| `Jinja2LikeEngine` | Control structures (`{% for %}`, `{% if %}`), filter pipeline (`|`), 12 built-in filters, autoescape |
| `MustacheEngine` | Logic-less templates with `{{#section}}`, `{{^inverted}}`, `{{{unescaped}}}`, `{{&unescaped}}` |
| `create_engine(engine_type)` | Factory function returning engine by name: `"simple"`, `"jinja2"`, `"mustache"` |

## Operating Contracts

- All engines implement the `TemplateEngine` ABC (`render` and `render_file` methods).
- `Jinja2LikeEngine` processes control structures before variable interpolation (for loops first, then if blocks, then variables).
- `MustacheEngine` processes sections before variables; sections iterate over lists, expand dicts, and invert on falsy values.
- `SimpleTemplateEngine` returns the original `{{ placeholder }}` text when a variable is not found in context; `Jinja2LikeEngine` returns empty string for missing variables.
- All engines support dotted path resolution (e.g., `user.name`).
- `Jinja2LikeEngine` condition evaluation supports `==`, `!=`, `>=`, `<=`, `>`, `<`, `in`, `not`, `and`, `or`.

## Integration Points

- Used by `templating.loaders.TemplateManager` for rendering registered templates.
- `TemplateEngine` is imported by `template_engine.py` which provides a higher-level `Template` wrapper and Jinja2/Mako backend support.

## Navigation

- [README](../README.md) | [SPEC](SPEC.md) | [PAI](PAI.md)
- Parent: [templating](../README.md)
