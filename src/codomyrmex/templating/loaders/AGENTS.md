# Codomyrmex Agents -- templating/loaders

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose

Template management layer providing named template registration, directory loading, template inheritance, batch rendering, and validation.

## Key Components

| Component | Role |
|-----------|------|
| `TemplateManager` | Registry of named templates with render, inheritance, batch, and validation operations |

## Operating Contracts

- `TemplateManager.__init__(engine="jinja2")` creates an internal `TemplateEngine` instance from `engines/template_engine.py`.
- Templates are stored as raw source strings keyed by name in `_templates: dict[str, str]`.
- `register(name, source, parent=None)` stores the template and optionally records a parent relationship for inheritance.
- `render(name, context)` renders the child template first, then injects its output into the parent's `{{ content }}` variable if a parent is defined.
- `load_directory(directory, extension=".html")` loads all matching files from a directory, using the filename stem as the template name.
- `validate(name)` attempts to render with an empty context; returns `(True, "")` on success or `(False, error_message)` on failure.
- `render_batch(name, contexts)` renders the same template with a list of context dicts.
- `remove_template(name)` also removes any parent relationship for that template.

## Integration Points

- Depends on `templating.engines.template_engine.Template` and `TemplateEngine` for rendering.
- Uses `logging_monitoring` for structured logging of register, add, and directory load operations.

## Navigation

- [README](../README.md) | [SPEC](SPEC.md) | [PAI](PAI.md)
- Parent: [templating](../README.md)
