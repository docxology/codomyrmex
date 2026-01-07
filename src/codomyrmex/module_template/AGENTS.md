# Codomyrmex Agents — src/codomyrmex/template

## Signposting
- **Parent**: [codomyrmex](../AGENTS.md)
- **Self**: [Agents](AGENTS.md)
- **Children**:
    - [docs](docs/AGENTS.md)
    - [tests](tests/AGENTS.md)
- **Key Artifacts**:
    - [Functional Spec](SPEC.md)
    - [Human Readme](README.md)

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Purpose
Template engine support (Jinja2, Mako) for code generation, documentation templates, and dynamic content. Provides template rendering, template loading, filter registration, and template management capabilities.

## Active Components
- `API_SPECIFICATION.md` – Detailed API specification
- `CHANGELOG.md` – Version history
- `MCP_TOOL_SPECIFICATION.md` – MCP tool specification
- `README.md` – Project file
- `SECURITY.md` – Security considerations
- `SPEC.md` – Project file
- `USAGE_EXAMPLES.md` – Usage examples
- `__init__.py` – Module exports and public API
- `docs/` – Directory containing docs components
- `requirements.template.txt` – Template requirements file
- `tests/` – Directory containing tests components

## Key Classes and Functions

### TemplateEngine (`__init__.py`)
- `TemplateEngine(engine_type: str = "jinja2")` – Template engine (Jinja2 or Mako)
- `render(template: str, context: dict) -> str` – Render template with context
- `load_template(template_path: str) -> Template` – Load template from file
- `register_filter(name: str, filter_func: callable) -> None` – Register custom filter
- `get_filter(name: str) -> Optional[callable]` – Get filter by name

### TemplateManager (`__init__.py`)
- `TemplateManager()` – Template management
- `register_template(name: str, template: Template) -> None` – Register template
- `get_template(name: str) -> Optional[Template]` – Get template by name

## Operating Contracts
- Maintain alignment between code, documentation, and configured workflows.
- Ensure Model Context Protocol interfaces remain available for sibling agents.
- Record outcomes in shared telemetry and update TODO queues when necessary.

## Navigation Links
- **Human Documentation**: [README.md](README.md)
- **Functional Specification**: [SPEC.md](SPEC.md)
- **📁 Parent Directory**: [codomyrmex](../README.md) - Parent directory documentation
- **🏠 Project Root**: [README](../../../README.md) - Main project documentation