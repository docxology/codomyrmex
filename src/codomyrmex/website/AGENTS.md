# Codomyrmex Agents — src/codomyrmex/website

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
Static website and dashboard generation for visualizing Codomyrmex ecosystem state. Provides flexible, template-based system for generating documentation and operational dashboards. Generates self-contained HTML/CSS/JS websites that visualize agent status, system metrics, workflow states, and operational data. Aggregates data from various system modules (agents, queue, build, etc.).

## Active Components
- `README.md` – Project file
- `SPEC.md` – Project file
- `API_SPECIFICATION.md` – Detailed API specification
- `__init__.py` – Module exports and public API
- `generator.py` – Main generation logic using Jinja2 templates
- `data_provider.py` – Data aggregation service from system modules
- `server.py` – HTTP server for serving generated websites
- `templates/` – Jinja2 HTML templates
- `assets/` – Static assets (CSS, JS, images)
- `docs/` – Directory containing docs components
- `tests/` – Directory containing tests components

## Key Classes and Functions

### WebsiteGenerator (`generator.py`)
- `WebsiteGenerator(output_dir: str, root_dir: Optional[str] = None)` – Generates static website
- `generate() -> None` – Execute generation process (renders templates, copies assets)
- `_render_page(template_name: str, context: dict) -> None` – Render individual page
- `_copy_assets() -> None` – Copy static assets to output directory

### DataProvider (`data_provider.py`)
- `DataProvider(root_dir: Path)` – Data aggregation service
- `get_system_summary() -> dict` – Get system summary data
- `get_agents_status() -> list[dict]` – Get agents status
- `get_available_scripts() -> list[dict]` – Get available scripts
- `get_config_files() -> list[dict]` – Get configuration files
- `get_doc_tree() -> dict` – Get documentation tree
- `get_pipeline_status() -> list[dict]` – Get pipeline status

### WebsiteServer (`server.py`)
- `WebsiteServer()` – Enhanced HTTP server with API endpoints
- `do_GET()` – Handle GET requests
- `do_POST()` – Handle API requests (execute, chat, refresh, config)

## Operating Contracts
- Output must be self-contained (no external CDN dependencies required for basic functionality unless specified).
- Interfaces must be responsive and accessible.
- All data aggregation must use proper module APIs.
- Templates must use Jinja2 syntax.