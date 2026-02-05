# website

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

Dynamic web dashboard and control interface for the Codomyrmex ecosystem. Generates a static website from Jinja2 templates, aggregates system data from multiple modules, and serves it via an HTTP server with API endpoints. Provides a central hub for viewing system status, executing scripts from the browser, chatting with local Ollama models, editing configuration files, browsing documentation, monitoring CI/CD pipelines, and listing agent definitions.

## Key Exports

- **`WebsiteGenerator`** -- Generates a static website from Jinja2 templates into a configurable output directory. Renders pages for the dashboard, documentation browser, configuration editor, pipeline visualization, and agent overview
- **`DataProvider`** -- Aggregates data from various Codomyrmex modules (system discovery, agents, configuration, pipelines) into a unified format consumed by the website templates and API endpoints
- **`WebsiteServer`** -- HTTP server with both static file serving and dynamic API endpoints for script execution, Ollama chat, configuration editing, and real-time system status queries

## Directory Contents

- `generator.py` -- `WebsiteGenerator` class with Jinja2 template rendering and static file output
- `data_provider.py` -- `DataProvider` class aggregating system data from discovery, agents, and config modules
- `server.py` -- `WebsiteServer` HTTP handler with API routes for dynamic functionality
- `templates/` -- Jinja2 HTML templates for dashboard, documentation, config editor, and other pages
- `assets/` -- Static assets (CSS, JavaScript, images) served by the website
- `requirements.template.txt` -- Template for website-specific Python dependencies

## Navigation

- **Full Documentation**: [docs/modules/website/](../../../docs/modules/website/)
- **Parent Directory**: [codomyrmex](../README.md)
- **Project Root**: ../../../README.md
