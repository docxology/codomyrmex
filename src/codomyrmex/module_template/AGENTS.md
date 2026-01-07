# Codomyrmex Agents — src/codomyrmex/module_template

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
Scaffolding and generation logic for creating new Codomyrmex modules. Ensures all new modules start with required structure, documentation files (README, AGENTS, SPEC), and configuration, enforcing Internal Coherence design principle. Uses template-driven approach with Jinja2 for generating files from templates. Supports idempotent module creation and upgrading existing folders to modules.

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

### ModuleGenerator (`__init__.py`)
- `ModuleGenerator()` – Module generation and scaffolding
- `create_module(name: str, human_name: str, **kwargs) -> bool` – Create new module with required structure
- `upgrade_module(module_path: str, force: bool = False) -> bool` – Upgrade existing folder to module (idempotent)
- `generate_scaffold(config: dict) -> dict` – Generate module scaffold from configuration

### TemplateRenderer (`__init__.py`)
- `TemplateRenderer()` – Template rendering for module files
- `render_template(template_name: str, context: dict) -> str` – Render template with context
- `load_template(template_path: str) -> Template` – Load template from file

### ScaffoldBuilder (`__init__.py`)
- `ScaffoldBuilder()` – Build module scaffold structure
- `create_structure(module_name: str, base_path: str) -> dict` – Create folder structure
- `generate_files(module_name: str, config: dict) -> list[str]` – Generate required files

## Operating Contracts
- Maintain alignment between code, documentation, and configured workflows.
- Ensure Model Context Protocol interfaces remain available for sibling agents.
- Record outcomes in shared telemetry and update TODO queues when necessary.

## Navigation Links
- **Human Documentation**: [README.md](README.md)
- **Functional Specification**: [SPEC.md](SPEC.md)
- **📁 Parent Directory**: [codomyrmex](../README.md) - Parent directory documentation
- **🏠 Project Root**: [README](../../../README.md) - Main project documentation