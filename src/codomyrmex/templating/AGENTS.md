# Codomyrmex Agents — src/codomyrmex/templating

## Signposting
- **Parent**: [codomyrmex](../AGENTS.md)
- **Self**: [Agents](AGENTS.md)
- **Children**:
    - None
- **Key Artifacts**:
    - [Functional Spec](SPEC.md)
    - [Human Readme](README.md)

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Purpose
Template engine support (Jinja2, Mako) for code generation, documentation templates, and dynamic content. Provides engine-agnostic template interface with support for template inheritance, custom filters, template caching, and loading templates from files or strings.

## Active Components
- `README.md` – Project file
- `SPEC.md` – Project file
- `__init__.py` – Module exports and public API
- `template_engine.py` – Template engine interface and implementations
- `template_manager.py` – Manager for template operations

## Key Classes and Functions

### TemplateEngine (`template_engine.py`)
- `TemplateEngine(engine: str = "jinja2")` – Initialize template engine with specified engine (jinja2, mako)
- `render(template: str, context: dict) -> str` – Render a template string with context data
- `load_template(path: str) -> Template` – Load a template from a file (with caching)
- `register_filter(name: str, func: Callable) -> None` – Register a custom template filter
- `get_filter(name: str) -> Optional[Callable]` – Get a registered filter
- `_render_jinja2(template: str, context: dict) -> str` – Internal Jinja2 rendering
- `_load_jinja2(path: str) -> Any` – Internal Jinja2 template loading
- `_render_mako(template: str, context: dict) -> str` – Internal Mako rendering
- `_load_mako(path: str) -> Any` – Internal Mako template loading

### Template (`template_engine.py`)
- `Template(template_obj: Any, engine: str)` – Template object wrapper
- `render(context: dict) -> str` – Render template with context

### TemplateManager (`template_manager.py`)
- `TemplateManager(engine: str = "jinja2")` – Manager for template operations
- `add_template(name: str, template: Union[str, Template]) -> None` – Add a template to the template manager
- `get_template(name: str) -> Optional[Template]` – Get a template by name
- `render(name: str, context: dict) -> str` – Render a template by name

### Module Functions (`__init__.py`)
- `render(template: str, context: dict, engine: str = "jinja2") -> str` – Render a template string with context
- `get_template_engine(engine: str = "jinja2") -> TemplateEngine` – Get a template engine instance

### Exceptions
- `TemplatingError` – Raised when templating operations fail

## Operating Contracts
- Maintain alignment between code, documentation, and configured workflows.
- Ensure Model Context Protocol interfaces remain available for sibling agents.
- Record outcomes in shared telemetry and update TODO queues when necessary.

## Navigation Links
- **Human Documentation**: [README.md](README.md)
- **Functional Specification**: [SPEC.md](SPEC.md)
- **📁 Parent Directory**: [codomyrmex](../README.md) - Parent directory documentation
- **🏠 Project Root**: [README](../../../README.md) - Main project documentation