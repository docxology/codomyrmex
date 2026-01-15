# Website Module

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## 1. Overview
The `website` module powers the documentation site and web interface for Codomyrmex. It includes a static site generator, a dynamic data provider, and a lightweight development server.

## 2. Core Components

### 2.1 Server (`server.py`)
A lightweight web server (typically Flask or FastAPI based) that serves the documentation and API reference. It supports hot-reloading for development.

### 2.2 Data Provider (`data_provider.py`)
Responsible for aggregating documentation, code metadata, and project statistics to be rendered by the website. It interfaces with the `api` and `scrape` modules to fetch real-time content.

### 2.3 Generator (`generator.py`)
A static site generation engine that compiles templates and markdown files into deployable HTML/CSS/JS assets.

### 2.4 Templates & Assets
- **`templates/`**: Jinja2 templates for page layouts (home, docs, api reference).
- **`assets/`**: Static resources including CSS, JavaScript, and images.

## 3. Usage

### Development Server
```bash
# Start the local dev server
python -m codomyrmex.website.server --debug
```

### Static Build
```bash
# Generate static site to output/site
python -m codomyrmex.website.generator --output ./output/site
```

## 4. MCP Integration
This module exposes Model Context Protocol (MCP) tools for interacting with the website during agent sessions. See [MCP_TOOL_SPECIFICATION.md](MCP_TOOL_SPECIFICATION.md) for details.

## 5. Navigation
- **Technical Documentation**: [AGENTS.md](AGENTS.md)
- **Functional Specification**: [SPEC.md](SPEC.md)
- **Parent Directory**: [codomyrmex](../README.md)
- **Project Root**: [README](../../../README.md)
