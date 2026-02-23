# Personal AI Infrastructure — Templating Module

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

The Templating module provides multi-engine template rendering with Jinja2 as the default backend. It supports context management, custom filters, and file-based templates for generating code, documentation, configurations, and reports.

## PAI Capabilities

### Template Rendering

```python
from codomyrmex.templating import render, render_file, get_default_engine

# Render an inline template
output = render("Hello {{ name }}!", context={"name": "PAI"})

# Render from a file
output = render_file("templates/report.md.j2", context={"modules": module_list})

# Get the engine instance
engine = get_default_engine("jinja2")
```

### Context and Filters

```python
from codomyrmex.templating import context, filters

# Context management for template data
# Custom filters for data transformation in templates
```

### Engine Backends

```python
from codomyrmex.templating import engines

# Jinja2 (default), with extensible engine interface
# Supports custom engine registration
```

## Key Exports

| Export | Type | Purpose |
|--------|------|---------|
| `render` | Function | Render inline template string with context |
| `render_file` | Function | Render template from file path |
| `get_default_engine` | Function | Get configured template engine instance |
| `context` | Module | Template context management |
| `filters` | Module | Custom template filter definitions |
| `engines` | Module | Template engine backends |
| `TemplatingError` | Exception | Templating-specific error |

## PAI Algorithm Phase Mapping

| Phase | Templating Contribution |
|-------|--------------------------|
| **BUILD** | Generate code files, configs, and documentation from templates |
| **EXECUTE** | Render reports and artifacts during workflow execution |
| **LEARN** | Generate structured output for knowledge capture |

## Architecture Role

**Core Layer** — Consumed by `documentation/` (doc generation), `ci_cd_automation/` (pipeline configs), `coding/` (code scaffolding), and `agents/` (prompt construction).

## Navigation

- **Self**: [PAI.md](PAI.md)
- **Parent**: [../PAI.md](../PAI.md) — Source-level PAI module map
- **Root Bridge**: [../../../PAI.md](../../../PAI.md) — Authoritative PAI system bridge doc
- **Siblings**: [README.md](README.md) | [AGENTS.md](AGENTS.md) | [SPEC.md](SPEC.md) | [API_SPECIFICATION.md](API_SPECIFICATION.md)
