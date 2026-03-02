# Template Loaders -- Technical Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

`TemplateManager` provides a unified API for template lifecycle: registration, retrieval, rendering (with inheritance), file-system loading, batch rendering, and validation.

## Architecture

```
loaders/
└── template_manager.py   # TemplateManager class
```

## TemplateManager API

### Registration and Retrieval

| Method | Signature | Description |
|--------|-----------|-------------|
| `register` | `(name: str, template_source: str, parent: str \| None = None) -> None` | Register template by name with optional parent |
| `add_template` | `(name: str, template: str \| Template) -> None` | Add template (accepts raw string or Template object) |
| `remove_template` | `(name: str) -> bool` | Remove template and its parent link; returns True if found |
| `has_template` | `(name: str) -> bool` | Check if template is registered |
| `list_templates` | `() -> list[str]` | Return sorted list of template names |
| `get_template` | `(name: str) -> str \| None` | Get template source by name |
| `get_parent` | `(name: str) -> str \| None` | Get parent template name |

### Rendering

| Method | Signature | Description |
|--------|-----------|-------------|
| `render` | `(name: str, context: dict \| None = None) -> str` | Render template; if parent defined, inject into parent's `{{ content }}` |
| `render_string` | `(template_source: str, context: dict \| None = None) -> str` | Render ad-hoc template string without registration |
| `render_batch` | `(name: str, contexts: list[dict]) -> list[str]` | Render same template with multiple contexts |

### File System Loading

| Method | Signature | Description |
|--------|-----------|-------------|
| `load_directory` | `(directory: str \| Path, extension: str = ".html") -> int` | Load all matching files from directory; returns count loaded |

### Validation and Summary

| Method | Signature | Description |
|--------|-----------|-------------|
| `validate` | `(name: str) -> tuple[bool, str]` | Render with empty context; returns (success, error_message) |
| `validate_all` | `() -> dict[str, tuple[bool, str]]` | Validate all registered templates |
| `template_count` | Property | Number of registered templates |
| `summary` | `() -> dict[str, Any]` | Returns `{"total": N, "with_parent": M, "names": [...]}` |

## Template Inheritance

Child templates extend parents via the `parent` parameter on `register()`. During `render()`:
1. Child template is rendered with the provided context.
2. Rendered child output is injected as `content` into the parent context.
3. Parent template is rendered with the merged context.

## Dependencies

- `templating.engines.template_engine.Template`, `TemplateEngine`
- `logging_monitoring.core.logger_config.get_logger`

## Error Handling

- `render()` raises `ValueError` if the template name is not found.
- `load_directory()` raises `FileNotFoundError` if the directory does not exist.

## Navigation

- [README](../README.md) | [AGENTS](AGENTS.md) | [PAI](PAI.md)
