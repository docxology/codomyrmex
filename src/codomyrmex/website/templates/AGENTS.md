# Codomyrmex Agents - src/codomyrmex/website/templates

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Purpose

The templates directory contains Jinja2 HTML templates for the Codomyrmex web dashboard. These templates use Jinja2 template inheritance with a base layout and page-specific content blocks, rendering dynamic data from the DataProvider.

## Active Components

- `base.html` - Base template with HTML structure, navigation, and common assets (CSS, JS, fonts, markdown rendering libraries, syntax highlighting)
- `index.html` - Dashboard page showing system status, module counts, agent counts, and quick actions
- `modules.html` - Module browser displaying all Codomyrmex packages with descriptions and submodules
- `scripts.html` - Script execution interface for running Python scripts from the scripts directory
- `chat.html` - Ollama chat interface for AI assistance
- `agents.html` - Agent integrations overview listing all AI agent frameworks
- `config.html` - Configuration file viewer and editor
- `docs.html` - Documentation browser with tree navigation
- `pipelines.html` - CI/CD pipeline status visualization
- `SPEC.md` - Template specification documentation

## Key Classes

Not applicable - this directory contains HTML templates, not Python classes.

## Operating Contracts

- All page templates extend `base.html` using `{% extends "base.html" %}`
- Content is placed in `{% block content %}` blocks
- Page titles are set via `{% block title %}` blocks
- Template variables are passed from WebsiteGenerator context:
  - `system` - System summary dict (status, version, environment, module_count, agent_count)
  - `modules` - List of module dicts (name, status, path, description, submodules)
  - `agents` - List of agent dicts (name, status, path, description, type)
  - `scripts` - List of script dicts (name, title, path, full_path, description)
  - `config_files` - List of config file dicts (name, path, type)
  - `doc_tree` - Nested documentation tree structure
  - `pipelines` - List of pipeline status dicts
- External resources: Google Fonts (Inter, Fira Code), Marked.js, DOMPurify, Highlight.js

## Signposting

- **Parent Directory**: [website/](../README.md) - Website generation module
- **Sibling Directories**:
  - [assets/](../assets/README.md) - Static CSS and JavaScript assets
- **Project Root**: [../../../../README.md](../../../../README.md) - Main project documentation
