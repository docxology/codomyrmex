# Website Module Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

The Website module provides a template-based system for generating dashboards, a live development server with 22 REST API endpoints, and operational tooling for the Codomyrmex project.

## Architecture

### Components

1. **Generator** (`generator.py`): Renders Jinja2 templates with data from DataProvider.
2. **Data Provider** (`data_provider.py`): Aggregates module, agent, script, config, pipeline, and PAI data.
3. **Server** (`server.py`): HTTP request handler with REST API endpoints and CORS/CSRF validation.
4. **Templates** (`templates/`): 12 Jinja2 HTML pages plus `base.html` layout.
5. **Assets** (`assets/`): CSS and JS static files.

### Data Flow

1. Generator instantiates DataProvider with project root path.
2. DataProvider scans the file system for modules, agents, scripts, configs, docs, pipelines, and PAI state.
3. Generator loads Jinja2 templates from the `templates/` directory.
4. Generator renders templates with collected data context.
5. Generator writes rendered HTML and copies assets to the output directory.

## Interfaces

### WebsiteGenerator

```python
class WebsiteGenerator:
    def __init__(self, output_dir: str, root_dir: str | None = None): ...
    def generate(self) -> None: ...
```

### DataProvider

```python
class DataProvider:
    def __init__(self, root_dir: Path): ...
    def get_system_summary(self) -> dict: ...
    def get_modules(self) -> list[dict]: ...
    def get_actual_agents(self) -> list[dict]: ...
    def get_available_scripts(self) -> list[dict]: ...
    def get_config_files(self) -> list[dict]: ...
    def get_config_content(self, filename: str) -> str: ...
    def save_config_content(self, filename: str, content: str) -> None: ...
    def get_doc_tree(self) -> dict: ...
    def get_doc_content(self, doc_path: str) -> str: ...
    def get_module_detail(self, name: str) -> dict | None: ...
    def get_health_status(self) -> dict: ...
    def get_pipeline_status(self) -> list[dict]: ...
    def get_pai_awareness_data(self) -> dict: ...
    def get_pai_missions(self) -> list[dict]: ...
    def get_pai_projects(self) -> list[dict]: ...
    def get_pai_tasks(self, project_id: str) -> list[dict]: ...
    def get_pai_telos(self) -> dict: ...
    def get_pai_memory_overview(self) -> dict: ...
    def get_mcp_tools(self) -> dict: ...
    def get_llm_config(self) -> dict: ...
    def run_tests(self, module: str | None = None) -> dict: ...
```

### WebsiteServer

```python
class WebsiteServer(http.server.SimpleHTTPRequestHandler):
    root_dir: Path
    data_provider: DataProvider | None
    def do_GET(self) -> None: ...
    def do_POST(self) -> None: ...
    def send_json_response(self, data: Any, status: int = 200) -> None: ...
```

## API Endpoints

| Endpoint | Method | Description |
| --- | --- | --- |
| `/api/status` | GET | System summary metrics |
| `/api/health` | GET | Comprehensive health data |
| `/api/modules` | GET | List all modules |
| `/api/modules/{name}` | GET | Module detail |
| `/api/agents` | GET | List AI agent integrations |
| `/api/scripts` | GET | List available scripts |
| `/api/config` | GET | List configuration files |
| `/api/config/{name}` | GET | Read config file content |
| `/api/config` | POST | Save config file content |
| `/api/docs` | GET | Documentation tree |
| `/api/docs/{path}` | GET | Doc file content |
| `/api/pipelines` | GET | CI/CD pipeline status |
| `/api/awareness` | GET | PAI ecosystem data |
| `/api/execute` | POST | Run a script |
| `/api/chat` | POST | Proxy to Ollama |
| `/api/tests` | POST | Run pytest suite |
| `/api/refresh` | POST | Refresh system summary, modules, agents, scripts |
| `/api/awareness/summary` | POST | Generate AI summary via Ollama |
| `/api/llm/config` | GET | Retrieve LLM configuration |
| `/api/tools` | GET | MCP tools, resources, prompts |
| `/api/trust/status` | GET | Trust gateway counts and destructive tools |
| `/api/pai/action` | POST | Execute PAI action (verify/trust/reset/status) |

## Dependencies

- **Jinja2**: Template rendering
- **PyYAML**: Workflow and config parsing
- **requests**: Ollama chat proxy
- **Standard Library**: `http.server`, `pathlib`, `json`, `shutil`, `subprocess`

## Navigation Links

- **Parent**: [Project Overview](../README.md)
- **Module Index**: [All Agents](../../AGENTS.md)
- **Documentation**: [Reference Guides](../../../docs/README.md)
- **Home**: [Root README](../../../README.md)

## Design Principles

1. **Strict Modularity**: Each component is isolated and communicates via well-defined APIs.
2. **Performance Optimization**: Lazy loading and intelligent caching minimize resource overhead.
3. **Error Resilience**: Robust exception handling ensures system stability.
4. **Extensibility**: Architecture accommodates future enhancements without breaking contracts.

## Testing

```bash
uv run python -m pytest src/codomyrmex/tests/unit/website/ -v
```
