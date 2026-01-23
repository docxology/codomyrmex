# Codomyrmex Agents - src/codomyrmex/templating

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Purpose

The Templating module provides template engine support for code generation, documentation templates, and dynamic content. It offers a unified interface for Jinja2 and Mako template engines with caching, custom filters, and consistent error handling.

## Active Components

- `__init__.py` - Module entry point with convenience functions `render()` and `get_template_engine()`
- `template_engine.py` - Core TemplateEngine class with multi-engine support (Jinja2, Mako)
- `template_manager.py` - TemplateManager for managing multiple named templates
- `API_SPECIFICATION.md` - API documentation
- `SPEC.md` - Technical specification

## Key Classes

- **TemplateEngine** - Template engine interface supporting multiple backends
  - `render(template, context)` - Render a template string with context data
  - `load_template(path)` - Load a template from file (with caching)
  - `register_filter(name, func)` - Register a custom template filter
  - `get_filter(name)` - Retrieve a registered filter
  - Supports `jinja2` and `mako` engines via constructor parameter

- **Template** - Wrapper around engine-specific template objects
  - `render(context)` - Render template with context, abstracting engine differences

- **TemplateManager** - Manager for template operations with named template storage
  - `add_template(name, template)` - Add a template (string or Template object)
  - `get_template(name)` - Retrieve a template by name
  - `render(name, context)` - Render a named template with context

- **TemplatingError** - Exception raised when templating operations fail

## Operating Contracts

- Default engine is `jinja2`; specify `mako` explicitly if needed
- Templates are cached by path for performance; cache is per-engine instance
- Custom filters are registered on the Jinja2 Environment
- Mako templates use `Template(filename=path)` for file-based loading
- TemplatingError wraps underlying engine exceptions with descriptive messages
- Missing engine packages raise TemplatingError with installation instructions

## Signposting

- **Parent Directory**: [codomyrmex](../README.md) - Main package documentation
- **Related Modules**:
  - [website/](../website/README.md) - Uses templating for web generation
- **Project Root**: [../../../README.md](../../../README.md) - Main project documentation
