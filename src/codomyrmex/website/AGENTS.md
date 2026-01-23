# Codomyrmex Agents - src/codomyrmex/website

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Purpose

The Website module provides a dynamic web dashboard and control interface for the Codomyrmex ecosystem. It serves as a central hub for human interaction with the system's data and operations, featuring a dashboard, script execution, Ollama chat integration, configuration editing, documentation browsing, and pipeline visualization.

## Active Components

- `__init__.py` - Module entry point exposing WebsiteGenerator, DataProvider, and WebsiteServer
- `generator.py` - Static website generation using Jinja2 templates
- `data_provider.py` - Data aggregation from system modules (modules, agents, scripts, configs, docs, pipelines)
- `server.py` - HTTP server with API endpoints for dynamic functionality
- `templates/` - Jinja2 HTML templates for all pages
- `assets/` - Static CSS, JavaScript, and other assets
- `API_SPECIFICATION.md` - API endpoint documentation
- `MCP_TOOL_SPECIFICATION.md` - Model Context Protocol tool specs
- `USAGE_EXAMPLES.md` - Usage examples and quick start guide
- `SECURITY.md` - Security considerations
- `CHANGELOG.md` - Version history
- `SPEC.md` - Technical specification

## Key Classes

- **WebsiteGenerator** - Generates static website from Jinja2 templates
  - `generate()` - Execute full generation process (prepare output, collect data, render pages, copy assets)
  - Renders pages: index.html, modules.html, scripts.html, chat.html, agents.html, config.html, docs.html, pipelines.html

- **DataProvider** - Aggregates data from various system modules
  - `get_system_summary()` - System status, version, environment, counts
  - `get_modules()` - Scan src/codomyrmex for all packages with descriptions
  - `get_actual_agents()` - List agent integrations from src/codomyrmex/agents
  - `get_available_scripts()` - Scan scripts directory for executable Python scripts
  - `get_config_files()` - Find configuration files (toml, yaml, json)
  - `get_doc_tree()` - Build documentation file tree
  - `get_pipeline_status()` - Retrieve CI/CD pipeline status

- **WebsiteServer** - HTTP server extending SimpleHTTPRequestHandler
  - POST `/api/execute` - Execute scripts from scripts directory
  - POST `/api/chat` - Proxy chat requests to Ollama
  - POST `/api/refresh` - Refresh system data
  - GET `/api/config` - List configuration files
  - GET `/api/config/<file>` - Get configuration file content
  - GET `/api/docs` - Get documentation tree
  - GET `/api/pipelines` - Get pipeline status

## Operating Contracts

- Script execution is sandboxed to the `scripts/` directory with path validation
- Configuration file access prevents directory traversal attacks
- Ollama chat proxying defaults to port 11434 with 60-second timeout
- Static generation clears and recreates output directory on each run
- Asset files are copied from `assets/` to output directory

## Signposting

- **Parent Directory**: [codomyrmex](../README.md) - Main package documentation
- **Submodules**:
  - [templates/](./templates/README.md) - Jinja2 HTML templates
  - [assets/](./assets/README.md) - Static CSS and JavaScript assets
- **Project Root**: [../../../README.md](../../../README.md) - Main project documentation
