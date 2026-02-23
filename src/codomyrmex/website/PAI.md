# Personal AI Infrastructure — Website Module

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

The Website module is the **human interface layer** for the Codomyrmex ecosystem. It provides a live web dashboard, REST API server, static site generator, and comprehensive data aggregation — making the entire system visible and interactive from a browser.

## PAI Capabilities

### Live Dashboard (Command Center)

The dashboard auto-refreshes from REST APIs every 15 seconds, providing real-time visibility into:

- **System metrics**: module count, agent count, script count, uptime, status
- **Git status**: branch, commits, dirty files, last commit
- **Documentation coverage**: API specs (87.7%), tests (88.7%), MCP specs (54.7%)
- **Architecture layers**: Foundation (4), Core (6), Service (5), Application (3), Extended (88)
- **MCP Server status**: probes `localhost:8080` for tool count, resources, prompts
- **PAI Awareness**: missions, projects, tasks, overall completion percentage

```python
from codomyrmex.website import WebsiteGenerator, WebsiteServer, DataProvider

# Generate static site from live data
gen = WebsiteGenerator(output_dir="/tmp/codomyrmex-site")
gen.generate()  # Renders all 10 pages from Jinja2 templates

# Start the API server
import socketserver
WebsiteServer.root_dir = Path("/path/to/codomyrmex")
WebsiteServer.data_provider = DataProvider(Path("/path/to/codomyrmex"))
with socketserver.TCPServer(("", 8787), WebsiteServer) as httpd:
    httpd.serve_forever()
```

### REST API (18 Endpoints)

The server exposes live data through REST endpoints:

| Endpoint | Method | PAI Algorithm Phase |
|----------|--------|-------------------|
| `/api/status` | GET | OBSERVE — system overview |
| `/api/health` | GET | VERIFY — system vitals, git, coverage |
| `/api/modules` | GET | OBSERVE — all 106 modules with metadata |
| `/api/modules/{name}` | GET | OBSERVE — module detail with README |
| `/api/agents` | GET | OBSERVE — agent integrations |
| `/api/scripts` | GET | OBSERVE — available scripts |
| `/api/config/{file}` | GET/POST | BUILD — read/edit config files |
| `/api/docs/{path}` | GET | OBSERVE — markdown documentation |
| `/api/pipelines` | GET | OBSERVE — CI/CD workflows |
| `/api/awareness` | GET | OBSERVE — PAI missions, projects, tasks |
| `/api/awareness/summary` | POST | THINK — AI-generated ecosystem summary |
| `/api/execute` | POST | EXECUTE — run scripts with output |
| `/api/tests` | POST | VERIFY — run pytest with JUnit XML parsing |
| `/api/chat` | POST | EXECUTE — Ollama LLM chat proxy |
| `/api/refresh` | POST | EXECUTE — regenerate site data |

### Data Aggregation (35+ Methods)

The `DataProvider` class aggregates data from across the project filesystem:

```python
from codomyrmex.website import DataProvider

dp = DataProvider(Path("/path/to/codomyrmex"))

# System-level data
dp.get_system_summary()       # module count, version, environment
dp.get_health_status()        # uptime, git, coverage, architecture
dp.get_modules()              # 106 modules with status, tests, specs

# Development data
dp.get_available_scripts()    # recursive script discovery
dp.get_actual_agents()        # agent integration discovery
dp.get_config_files()         # project config files
dp.get_doc_tree()             # documentation hierarchy
dp.get_pipeline_status()      # GitHub Actions workflow parsing

# PAI ecosystem data
dp.get_pai_awareness_data()   # missions, projects, tasks, Telos
dp.run_tests()                # execute pytest, parse JUnit XML results
```

### 10 Interactive Pages

| Page | Template | Features |
|------|----------|----------|
| **Dashboard** | `index.html` | Live metrics, MCP status, PAI summary, quick actions |
| **Health** | `health.html` | System vitals, git info, coverage bars, test runner |
| **Modules** | `modules.html` | Searchable grid of 106 modules with status badges |
| **Scripts** | `scripts.html` | Searchable script cards with inline execution |
| **Agents** | `agents.html` | AI agent integration catalog |
| **Chat** | `chat.html` | Ollama LLM chat interface |
| **Config** | `config.html` | File browser with inline editor and save |
| **Docs** | `docs.html` | Markdown documentation browser with syntax highlighting |
| **Pipelines** | `pipelines.html` | CI/CD workflow visualization |
| **Awareness** | `awareness.html` | PAI missions, projects, tasks, Mermaid dependency graph |

### Security Features

- **Origin validation**: `_ALLOWED_ORIGINS` restricts CORS to localhost
- **Path traversal protection**: blocks `..` and absolute paths in script/config/doc access
- **Safe file extensions**: config editing restricted to `.toml`, `.yaml`, `.json`, `.txt`, `.cfg`, `.ini`
- **Script sandboxing**: execution limited to `scripts/` directory with 300s timeout
- **Test locking**: prevents concurrent test executions (HTTP 429)

## PAI Algorithm Phase Mapping

| Phase | Website Module Contribution |
|-------|---------------------------|
| **OBSERVE** | `/api/modules`, `/api/health`, `/api/awareness` — gather system state |
| **THINK** | `/api/awareness/summary` — AI ecosystem analysis via Ollama |
| **PLAN** | Dashboard coverage data informs what needs work |
| **BUILD** | `/api/config` — edit configuration, `/api/execute` — run scripts |
| **EXECUTE** | `/api/execute`, `/api/chat` — script execution, LLM interaction |
| **VERIFY** | `/api/tests` — run pytest suite, `/api/health` — check system status |
| **LEARN** | Awareness page tracks mission/project progress over time |

## MCP Server Integration

The dashboard probes the MCP server at `localhost:8080` and displays:
- Tool count (33), resource count, prompt count
- Server status (online/offline)
- Direct link to the MCP Web UI

## Key Classes

| Class | File | Purpose |
|-------|------|---------|
| `WebsiteGenerator` | `generator.py` | Jinja2 static site generation (10 pages) |
| `DataProvider` | `data_provider.py` | Data aggregation (35+ methods, 1122 lines) |
| `WebsiteServer` | `server.py` | HTTP server with 18 REST API endpoints |

## Accessibility

- Skip link for keyboard navigation
- ARIA labels on interactive elements (`aria-current`, `aria-busy`, `aria-expanded`)
- Keyboard shortcuts: Alt+1 through Alt+9, Alt+0
- Connection status indicators with semantic classes
- Responsive design (mobile breakpoints at 900px and 600px)

## Navigation

- **Self**: [PAI.md](PAI.md)
- **Parent**: [../PAI.md](../PAI.md) — Source-level PAI module map
- **Root Bridge**: [../../../PAI.md](../../../PAI.md) — Authoritative PAI system bridge doc
- **Siblings**: [README.md](README.md) | [AGENTS.md](AGENTS.md) | [SPEC.md](SPEC.md) | [API_SPECIFICATION.md](API_SPECIFICATION.md)
- **MCP Bridge**: [../model_context_protocol/PAI.md](../model_context_protocol/PAI.md)
