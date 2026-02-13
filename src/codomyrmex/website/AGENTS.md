# Agent Guidelines - Website

**Type**: Application Module
**Status**: Active
**Version**: v0.2.0

## Module Overview

The Website module serves as the primary user interface for the Codomyrmex ecosystem. While not an autonomous agent itself, it acts as a critical interface layer (Human-in-the-Loop) for interacting with agents, monitoring system health, and managing configurations.

## Capabilities

1. **Observability**: Real-time dashboard for system metrics (CPU, Memory, Uptime) and Git status.
2. **Agent Interaction**: Direct chat interface for interacting with LLM agents via Ollama.
3. **Documentation Browser**: Rendered view of project documentation and specifications.
4. **Configuration Management**: Web-based editor for system configuration files.
5. **Task Execution**: Trigger scripts and workflows directly from the UI.
6. **PAI Awareness**: Visualization of the Personal AI Infrastructure (Missions, Projects, Tasks).

## Key Classes

- **WebsiteGenerator**: Renders Jinja2 templates into a static site.
- **DataProvider**: Aggregates module, agent, script, config, and PAI data.
- **WebsiteServer**: HTTP request handler with 19 REST API endpoints.

## Integration Points

- **Data Provider**: Aggregates data from `src/codomyrmex/` and `.claude/` directories.
- **Ollama**: Proxies chat requests to local LLM inference server via `http://localhost:11434`.
- **Scripts**: Discovers and executes scripts from `scripts/`.
- **CI/CD**: Monitors `.github/workflows` status.

## Usage

### Starting the Dashboard

```bash
uv run python -m codomyrmex.website.server
```

Access at: `http://localhost:8787`

### API Interaction

The module exposes a REST API for external integrations. Key endpoints include:

- `GET /api/status`: System health check.
- `GET /api/llm/config`: Retrieve current LLM configuration.
- `POST /api/chat`: Send message to active agent/LLM.
- `POST /api/execute`: Run a registered script.

## Development

The frontend is built with vanilla HTML/JS/CSS for maximum performance and zero build-step requirements.

- **Templates**: `src/codomyrmex/website/templates/`
- **Assets**: `src/codomyrmex/website/assets/`
- **Logic**: `src/codomyrmex/website/server.py` and `data_provider.py`

## Common Patterns

```python
import socketserver
from codomyrmex.website import WebsiteGenerator, DataProvider, WebsiteServer

# Generate static website
generator = WebsiteGenerator(output_dir="./build", root_dir=".")
generator.generate()

# Start development server
WebsiteServer.root_dir = Path(".")
WebsiteServer.data_provider = DataProvider(Path("."))
with socketserver.TCPServer(("", 8787), WebsiteServer) as httpd:
    httpd.serve_forever()
```
