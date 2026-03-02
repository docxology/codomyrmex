# Template Engines -- Technical Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

Three template engine implementations sharing a common ABC, plus a factory function for engine selection.

## Architecture

```
engines/
├── __init__.py          # TemplateContext, 3 engines, create_engine()
└── template_engine.py   # Template wrapper, TemplateEngine with Jinja2/Mako backend
```

## Key Classes

### TemplateContext

| Method | Signature | Description |
|--------|-----------|-------------|
| `get` | `(key: str, default=None) -> Any` | Look up key in data, then parent chain |
| `set` | `(key: str, value: Any) -> None` | Set value in current context |
| `child` | `(**kwargs) -> TemplateContext` | Create child context with this as parent |

### SimpleTemplateEngine

| Method | Signature | Description |
|--------|-----------|-------------|
| `__init__` | `(delimiters=("{{","}}"), escape_html=False)` | Configure delimiters and escaping |
| `render` | `(template: str, context: dict) -> str` | Regex-based interpolation with dotted paths |
| `render_file` | `(path: str, context: dict) -> str` | Load file and render |

### Jinja2LikeEngine

| Method | Signature | Description |
|--------|-----------|-------------|
| `__init__` | `(filters=None, autoescape=True)` | Register custom filters, configure HTML escaping |
| `render` | `(template: str, context: dict) -> str` | Process for loops, if blocks, then variables |
| `render_file` | `(path: str, context: dict) -> str` | Load file and render |

Built-in filters: `upper`, `lower`, `title`, `strip`, `length`, `default`, `safe`, `escape`, `join`, `first`, `last`, `reverse`, `sort`.

For-loop context variables: `loop.index` (1-based), `loop.index0`, `loop.first`, `loop.last`, `loop.length`.

### MustacheEngine

| Method | Signature | Description |
|--------|-----------|-------------|
| `render` | `(template: str, context: dict) -> str` | Process sections then variables |
| `render_file` | `(path: str, context: dict) -> str` | Load file and render |

Section types: `{{#truthy}}` (iterate lists, expand dicts), `{{^inverted}}` (render on falsy), `{{{unescaped}}}` and `{{&unescaped}}` (no HTML escaping).

### Factory

```python
create_engine("simple")    # -> SimpleTemplateEngine
create_engine("jinja2")    # -> Jinja2LikeEngine
create_engine("mustache")  # -> MustacheEngine
```

## Dependencies

- Python `re`, `html` (standard library)
- No external template library dependencies

## Constraints

- Nested for loops are processed iteratively (innermost first via `while pattern.search`).
- `Jinja2LikeEngine` condition evaluation uses string splitting, not a full expression parser; complex nested expressions may not evaluate correctly.
- `MustacheEngine` does not support partials or lambdas.

## Navigation

- [README](../README.md) | [AGENTS](AGENTS.md) | [PAI](PAI.md)
