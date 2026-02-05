# templating

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

The templating module provides template engine support for code generation, documentation templates, and dynamic content rendering. It supports Jinja2 and Mako engines through a unified interface, with convenience functions for rendering template strings and files, custom filter support, configurable template loaders, and a template manager for organized template collections.

## Key Exports

### Submodules (always available)

- **`engines`** -- Template engine implementations (Jinja2, Mako)
- **`filters`** -- Custom template filters for data transformation
- **`context`** -- Template context management and variable injection

### Functions

- **`render()`** -- Convenience function to render a template string with context data using a specified engine (defaults to Jinja2). Example: `render("Hello {{ name }}!", {"name": "World"})`
- **`render_file()`** -- Load and render a template file from disk with context data and optional engine selection.
- **`get_default_engine()`** -- Get or create the default template engine instance, with lazy initialization and engine type switching.

### Classes (conditionally available)

- **`TemplateEngine`** -- Core engine class supporting Jinja2 and Mako rendering backends. Provides `render()` and `load_template()` methods.
- **`Template`** -- Represents a loaded, renderable template with context binding.
- **`TemplateManager`** -- Manages template collections, loading from directories via configurable template loaders.
- **`TemplatingError`** -- Exception raised when templating operations fail. Extends `CodomyrmexError`.

## Directory Contents

- `__init__.py` - Module entry point with convenience functions and conditional class exports
- `engines/` - Template engine implementations (`template_engine.py`)
- `filters/` - Custom template filter definitions
- `context/` - Template context management
- `loaders/` - Template loading and management (`template_manager.py`)
- `AGENTS.md` - Agent integration specification
- `API_SPECIFICATION.md` - Programmatic interface documentation
- `SPEC.md` - Module specification
- `PAI.md` - PAI integration notes

## Navigation

- **Full Documentation**: [docs/modules/templating/](../../../docs/modules/templating/)
- **Parent Directory**: [codomyrmex](../README.md)
- **Project Root**: ../../../README.md
