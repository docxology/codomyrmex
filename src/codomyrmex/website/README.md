# Website Module

**Version**: v0.1.0 | **Status**: Active

Dynamic web dashboard and control interface for Codomyrmex.

## Quick Start

```python
import socketserver
from codomyrmex.website import WebsiteGenerator, DataProvider, WebsiteServer

# Generate static website
generator = WebsiteGenerator(output_dir="./build")
generator.generate()

# Start development server (WebsiteServer is a request handler, not a standalone server)
WebsiteServer.data_provider = DataProvider()
with socketserver.TCPServer(("", 8787), WebsiteServer) as httpd:
    print("Serving at http://localhost:8787")
    httpd.serve_forever()
```

## Features

- **Dashboard** — System status, module health, quick actions
- **Documentation Browser** — Browse all README/SPEC/AGENTS files
- **Configuration Editor** — Edit YAML/JSON configs in browser
- **Pipeline Visualization** — CI/CD pipeline status
- **Ollama Chat** — Chat with local LLM models
- **Agent Overview** — List all agent definitions

## Exports

| Class | Description |
|-------|-------------|
| `WebsiteGenerator` | Generate static site from Jinja2 templates |
| `DataProvider` | Aggregate data from Codomyrmex modules |
| `WebsiteServer` | HTTP server with API endpoints |

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/status` | GET | System health status |
| `/api/config` | GET/POST | Read/write configuration |
| `/api/chat` | POST | Chat with Ollama |
| `/api/scripts/run` | POST | Execute scripts |

## Directory Structure

| Path | Description |
|------|-------------|
| `generator.py` | Static site generator |
| `data_provider.py` | Data aggregation |
| `server.py` | HTTP server |
| `templates/` | Jinja2 HTML templates |
| `assets/` | CSS, JS, images |


## Testing

```bash
uv run python -m pytest src/codomyrmex/tests/ -k website -v
```


## Documentation

- [Module Documentation](../../../docs/modules/website/README.md)
- [Agent Guide](../../../docs/modules/website/AGENTS.md)
- [Specification](../../../docs/modules/website/SPEC.md)

## Navigation

- [SPEC](SPEC.md) | [AGENTS](AGENTS.md) | [PAI](PAI.md)
