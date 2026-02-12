# Website Module

**Version**: v0.2.0 | **Status**: Active

Dynamic web dashboard and control interface for Codomyrmex.

## Quick Start

```python
import socketserver
from pathlib import Path
from codomyrmex.website import WebsiteGenerator, DataProvider, WebsiteServer

# Generate static website
generator = WebsiteGenerator(output_dir="./build")
generator.generate()

# Start development server (WebsiteServer is a request handler, not a standalone server)
WebsiteServer.root_dir = Path(".")
WebsiteServer.data_provider = DataProvider(Path("."))
with socketserver.TCPServer(("", 8787), WebsiteServer) as httpd:
    print("Serving at http://localhost:8787")
    httpd.serve_forever()
```

## Features

- **Dashboard** — System status, module health, architecture layers, quick actions
- **Health** — Comprehensive system health with test runner
- **Modules** — Browse all Codomyrmex packages with detail views
- **Scripts** — Execute scripts from the browser with real-time output
- **Configuration Editor** — Edit YAML/JSON/TOML configs in browser
- **Documentation Browser** — Navigate and view all README/SPEC/AGENTS files
- **Pipeline Visualization** — CI/CD workflow status from `.github/workflows/`
- **Agents** — List all AI agent integrations
- **Ollama Chat** — Chat with local LLM models
- **PAI Awareness** — Mission/project/task dashboard with Mermaid graphs

## Exports

| Class | Description |
|-------|-------------|
| `WebsiteGenerator` | Generate static site from Jinja2 templates |
| `DataProvider` | Aggregate data from Codomyrmex modules |
| `WebsiteServer` | HTTP server with 18 API endpoints |

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
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
| `/api/refresh` | POST | Refresh system data |
| `/api/awareness/summary` | POST | Generate AI summary |

## Directory Structure

| Path | Description |
|------|-------------|
| `generator.py` | Static site generator |
| `data_provider.py` | Data aggregation layer (1122 lines) |
| `server.py` | HTTP server with REST API |
| `templates/` | 10 Jinja2 HTML templates + base layout |
| `assets/` | CSS and JS static files |

## Testing

```bash
uv run python -m pytest src/codomyrmex/tests/unit/website/ -v
```

## Documentation

- [Module Documentation](../../../docs/modules/website/README.md)
- [Agent Guide](../../../docs/modules/website/AGENTS.md)
- [Specification](../../../docs/modules/website/SPEC.md)

## Navigation

- [SPEC](SPEC.md) | [AGENTS](AGENTS.md) | [PAI](PAI.md)
