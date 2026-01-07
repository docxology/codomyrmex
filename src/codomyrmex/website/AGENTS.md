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
- `README.md` – Human-readable documentation
- `SPEC.md` – Functional specification
- `API_SPECIFICATION.md` – API endpoint documentation
- `__init__.py` – Module exports (WebsiteGenerator, DataProvider, WebsiteServer)
- `generator.py` – Static website generation using Jinja2 templates
- `data_provider.py` – Data aggregation from system modules
- `server.py` – HTTP server with dynamic API endpoints
- `templates/` – Jinja2 HTML templates (8 pages)
- `assets/` – Static assets (CSS, JS)
- `docs/` – Additional documentation
- `tests/` – Unit and integration tests

## Key Classes and Functions

### WebsiteGenerator (`generator.py`)
```python
class WebsiteGenerator:
    def __init__(self, output_dir: str, root_dir: Optional[str] = None): ...
    def generate(self) -> None: ...
    def _render_page(template_name: str, context: dict) -> None: ...
    def _copy_assets() -> None: ...
```

### DataProvider (`data_provider.py`)
```python
class DataProvider:
    def __init__(self, root_dir: Path): ...
    def get_system_summary() -> dict: ...
    def get_agents_status() -> list[dict]: ...
    def get_available_scripts() -> list[dict]: ...
    def get_config_files() -> list[dict]: ...
    def get_config_content(filename: str) -> str: ...
    def save_config_content(filename: str, content: str) -> None: ...
    def get_doc_tree() -> dict: ...
    def get_pipeline_status() -> list[dict]: ...
```

### WebsiteServer (`server.py`)
```python
class WebsiteServer(http.server.SimpleHTTPRequestHandler):
    root_dir: Path  # Class attribute
    data_provider: DataProvider  # Class attribute
    
    def do_GET() -> None: ...
    def do_POST() -> None: ...
    def handle_execute() -> None: ...
    def handle_chat() -> None: ...
    def handle_refresh() -> None: ...
    def handle_config_list() -> None: ...
    def handle_config_get(path: str) -> None: ...
    def handle_config_save() -> None: ...
    def handle_docs_list() -> None: ...
    def handle_pipelines_list() -> None: ...
    def send_json_response(data: dict, status: int = 200) -> None: ...
```

## Frontend Features

### Markdown Rendering
- Uses `marked.js` for client-side markdown parsing
- Syntax highlighting via `highlight.js` (Python, JavaScript, Bash, JSON)
- HTML sanitization via `DOMPurify`

### Scripts Page
- Search/filter functionality
- Improved card layout with script path and description
- Console output for execution results

### Config Editor
- File type icons
- Auto-select first file on load
- Save functionality with server-side persistence

## Test Coverage

### Unit Tests (`tests/unit/`)
- `test_generator.py` - 11 tests for WebsiteGenerator
- `test_data_provider.py` - 31 tests for DataProvider
- `test_server.py` - 13 tests for WebsiteServer

### Integration Tests (`tests/integration/`)
- `test_website_integration.py` - 10 tests for end-to-end functionality

**Total: 64 tests** (all passing)

## Operating Contracts
- Output must be self-contained (no external CDN dependencies required for basic functionality unless specified).
- Interfaces must be responsive and accessible.
- All data aggregation must use proper module APIs.
- Templates must use Jinja2 syntax.
- Path traversal attacks must be prevented in config operations.
- Scripts can only be executed from within the `scripts/` directory.

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/execute` | POST | Execute a script |
| `/api/chat` | POST | Chat with Ollama |
| `/api/refresh` | POST | Refresh system data |
| `/api/config` | GET | List config files |
| `/api/config/{file}` | GET/POST | Read/write config |
| `/api/docs` | GET | Get doc tree |
| `/api/pipelines` | GET | Get pipeline status |