# Website Generation Module

**Package**: `src.codomyrmex.website`  
**Layer**: Service Layer  
**Version**: v0.1.0

## Purpose

This module provides a dynamic web dashboard and control interface for the Codomyrmex ecosystem. It serves as a central hub for human interaction with the system's data and operations.

## Key Features

- **Dashboard**: View system status, agent counts, and environment details.
- **Script Execution**: Run any script from the `scripts/` directory directly from the browser.
- **Ollama Chat**: Interact with local Ollama models for AI assistance.
- **Configuration Editor**: View and edit configuration files (`.toml`, `.yaml`, `.json`).
- **Documentation Browser**: Navigate and view project documentation with full markdown rendering.
- **Pipeline Visualization**: Monitor CI/CD pipeline status.
- **Agent Overview**: List all agents with their descriptions and paths.

## Quick Start

### 1. Generate and Serve

You can generate, serve, and open the website in one command:

```bash
# Generate, serve, and open in browser
python scripts/website/generate.py --open

# Just generate and serve
python scripts/website/generate.py --serve

# Generate only (default)
python scripts/website/generate.py
```

### 2. Manual Serving

If you prefer to serve the website separately:

```bash
python scripts/website/serve.py
```

The server starts at `http://localhost:8000` with API endpoints active.

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/execute` | POST | Execute a script from `scripts/` |
| `/api/chat` | POST | Chat with Ollama |
| `/api/refresh` | POST | Refresh system data |
| `/api/config` | GET | List configuration files |
| `/api/config/{file}` | GET/POST | Read/write config files |
| `/api/docs` | GET | Get documentation tree |
| `/api/pipelines` | GET | Get pipeline status |

## Components

### `generator.py`

`WebsiteGenerator` - Renders Jinja2 templates into static HTML pages.

```python
from codomyrmex.website import WebsiteGenerator

generator = WebsiteGenerator(output_dir="./output/website")
generator.generate()
```

### `server.py`

`WebsiteServer` - HTTP server with dynamic API endpoints.

```python
import socketserver
from codomyrmex.website import WebsiteServer, DataProvider

WebsiteServer.root_dir = Path(".")
WebsiteServer.data_provider = DataProvider(Path("."))

with socketserver.TCPServer(("", 8000), WebsiteServer) as httpd:
    httpd.serve_forever()
```

### `data_provider.py`

`DataProvider` - Aggregates data from the project (agents, scripts, configs, docs).

```python
from codomyrmex.website import DataProvider

provider = DataProvider(root_dir=Path("."))

# Get system summary
system = provider.get_system_summary()

# Get all agents
agents = provider.get_agents_status()

# Get available scripts
scripts = provider.get_available_scripts()

# Get configuration files
configs = provider.get_config_files()

# Get documentation tree
docs = provider.get_doc_tree()

# Get pipeline status
pipelines = provider.get_pipeline_status()
```

## Frontend Features

### Markdown Rendering

The documentation browser uses [marked.js](https://marked.js.org/) for client-side markdown rendering with:
- GitHub Flavored Markdown (GFM) support
- Syntax highlighting via [highlight.js](https://highlightjs.org/)
- HTML sanitization via [DOMPurify](https://github.com/cure53/DOMPurify)

### Script Filtering

The scripts page includes a search/filter feature to quickly find scripts by name.

### Configuration Editor

The config editor supports:
- Multiple file types (TOML, YAML, JSON, TXT)
- Syntax-highlighted editing with monospace font
- Save functionality with server-side persistence

## Testing

### Run Unit Tests

```bash
python -m pytest src/codomyrmex/website/tests/unit/ -v
```

### Run Integration Tests

```bash
python -m pytest src/codomyrmex/website/tests/integration/ -v
```

### Run All Tests

```bash
python -m pytest src/codomyrmex/website/tests/ -v
```

## Template Structure

```
templates/
├── base.html       # Base template with navigation and common elements
├── index.html      # Dashboard homepage
├── scripts.html    # Script orchestration page
├── chat.html       # Ollama chat interface
├── agents.html     # Agent overview
├── config.html     # Configuration editor
├── docs.html       # Documentation browser
└── pipelines.html  # CI/CD pipeline visualization
```

## Assets

```
assets/
├── css/
│   └── style.css   # Main stylesheet with dark theme
└── js/
    └── app.js      # Client-side JavaScript for interactivity
```

## Security Considerations

- **Path Traversal Protection**: Config read/write operations validate paths to prevent access outside the project root.
- **Script Execution Safety**: Only scripts within the `scripts/` directory can be executed.
- **HTML Sanitization**: All markdown content is sanitized with DOMPurify before rendering.

## Dependencies

- `jinja2` - Template rendering
- `requests` - Ollama API integration

## Contributing

See the [AGENTS.md](AGENTS.md) file for technical documentation and contribution guidelines.
