# Codomyrmex Agents — src/codomyrmex/templating

## Signposting
- **Parent**: [codomyrmex](../AGENTS.md)
- **Self**: [Templating Agents](AGENTS.md)
- **Children**:
    - None
- **Key Artifacts**:
    - [Functional Spec](SPEC.md)
    - [Human Readme](README.md)

**Version**: v0.1.0 | **Status**: Proposed | **Last Updated**: December 2025

## Purpose

Templating module providing template engine support (Jinja2, Mako) for code generation, documentation templates, and dynamic content for the Codomyrmex platform. This module consolidates `template/` and `module_template/` functionality.

The templating module serves as the templating layer, providing engine-agnostic template interfaces with support for multiple template engines.

## Module Overview

### Key Capabilities
- **Template Rendering**: Render templates with context data
- **Template Loading**: Load templates from files or strings
- **Template Caching**: Cache compiled templates for performance
- **Template Inheritance**: Support template inheritance and includes
- **Custom Filters**: Register custom template filters

### Key Features
- Engine-agnostic template interface
- Support for multiple template engines
- Template caching for performance
- Template inheritance support
- Custom filter registration

## Function Signatures

### Template Rendering Functions

```python
def render(template: str, context: dict) -> str
```

Render a template string with context data.

**Parameters:**
- `template` (str): Template string
- `context` (dict): Context data for template

**Returns:** `str` - Rendered template

**Raises:**
- `TemplatingError`: If rendering fails

```python
def load_template(path: str) -> Template
```

Load a template from a file.

**Parameters:**
- `path` (str): Template file path

**Returns:** `Template` - Template object

**Raises:**
- `TemplatingError`: If template loading fails

```python
def render_template(template: Template, context: dict) -> str
```

Render a loaded template with context.

**Parameters:**
- `template` (Template): Template object
- `context` (dict): Context data

**Returns:** `str` - Rendered template

### Filter Functions

```python
def register_filter(name: str, func: callable) -> None
```

Register a custom template filter.

**Parameters:**
- `name` (str): Filter name
- `func` (callable): Filter function

```python
def get_filter(name: str) -> Optional[callable]
```

Get a registered filter.

**Parameters:**
- `name` (str): Filter name

**Returns:** `Optional[callable]` - Filter function if found

### Template Management Functions

```python
def add_template(name: str, template: str | Template) -> None
```

Add a template to the template manager.

**Parameters:**
- `name` (str): Template name
- `template` (str | Template): Template string or object

```python
def get_template(name: str) -> Optional[Template]
```

Get a template by name.

**Parameters:**
- `name` (str): Template name

**Returns:** `Optional[Template]` - Template object if found

## Active Components

### Core Implementation
- `__init__.py` – Module initialization and public API exports
- `template_engine.py` – Base template engine interface
- `template_manager.py` – Template management and caching
- `engines/` – Engine-specific implementations
  - `jinja2_engine.py` – Jinja2 engine
  - `mako_engine.py` – Mako engine

### Documentation
- `README.md` – Module usage and overview
- `AGENTS.md` – This file: agent documentation
- `SPEC.md` – Functional specification

## Operating Contracts

### Universal Templating Protocols

All templating operations within the Codomyrmex platform must:

1. **Error Handling** - Handle template errors gracefully
2. **Template Validation** - Validate templates before rendering
3. **Caching** - Cache compiled templates for performance
4. **Security** - Sanitize template context to prevent injection
5. **Performance** - Optimize template compilation and rendering

### Integration Guidelines

When integrating with other modules:

1. **Use Module Template** - Integrate with module_template for code generation
2. **Documentation Integration** - Support documentation module for doc templates
3. **Code Generation** - Support code module for code generation templates
4. **Error Recovery** - Implement fallback when template rendering fails

## Navigation Links

- **Human Documentation**: [README.md](README.md)
- **Functional Specification**: [SPEC.md](SPEC.md)

### Module Documentation
- **Module Overview**: [README.md](README.md) - Complete module documentation

### Platform Navigation
- **Parent Directory**: [codomyrmex](../README.md) - Package overview
- **Project Root**: [README](../../../README.md) - Main project documentation
- **Related Modules**:
    - [module_template](../module_template/AGENTS.md) - Module templates
    - [documentation](../documentation/AGENTS.md) - Documentation generation

