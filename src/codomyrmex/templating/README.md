# Templating Module

**Version**: v0.1.0 | **Status**: Active

Template engine support (Jinja2, Mako) for code generation and dynamic content.


## Installation

```bash
pip install codomyrmex
```

Or for development:

```bash
uv sync
```

## Key Exports

### Classes
- **`TemplatingError`** — Raised when templating operations fail.

### Functions
- **`get_default_engine()`** — Get or create default template engine instance.
- **`render()`** — Render a template string with context data.
- **`render_file()`** — Load and render a template file.

### Submodules
- **`context/`** — Context builders submodule.
- **`engines/`** — Template engine implementations.
- **`filters/`** — Template filters submodule.
- **`loaders/`** — Template loaders submodule.

## Quick Start

```python
from codomyrmex.templating import render, render_file, TemplateEngine

# Simple template rendering
result = render("Hello {{ name }}!", {"name": "World"})
print(result)  # Hello World!

# Render from file
output = render_file("templates/email.html", {
    "recipient": "John",
    "subject": "Welcome"
})

# Use specific engine
jinja_output = render("{% for i in items %}{{ i }}{% endfor %}", 
                      {"items": [1, 2, 3]}, engine="jinja2")

# Use TemplateEngine directly
from codomyrmex.templating import TemplateEngine

engine = TemplateEngine(engine="jinja2")
template = engine.load_template("report.html.j2")
result = template.render({"data": report_data})
```

## Exports

| Item | Description |
|------|-------------|
| `render(template, context)` | Render template string |
| `render_file(path, context)` | Render template file |
| `get_default_engine()` | Get singleton engine instance |
| `TemplateEngine` | Configurable template engine |
| `Template` | Loaded template object |
| `TemplateManager` | Template directory management |

## Submodules

- `engines/` — Jinja2 and Mako engine implementations
- `filters/` — Custom template filters
- `context/` — Context processors
- `loaders/` — Template loaders

## Engines

| Engine | Syntax | Best For |
|--------|--------|----------|
| jinja2 | `{{ }}` | HTML, configs, general |
| mako | `${}` | Python-heavy templates |


## Testing

```bash
uv run python -m pytest src/codomyrmex/tests/ -k templating -v
```


## Documentation

- [Module Documentation](../../../docs/modules/templating/README.md)
- [Agent Guide](../../../docs/modules/templating/AGENTS.md)
- [Specification](../../../docs/modules/templating/SPEC.md)

## Navigation

- [SPEC](SPEC.md) | [AGENTS](AGENTS.md) | [PAI](PAI.md)
