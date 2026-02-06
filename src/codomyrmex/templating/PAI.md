# Personal AI Infrastructure — Templating Module

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

The Templating module provides PAI integration for template rendering.

## PAI Capabilities

### Template Rendering

Render templates:

```python
from codomyrmex.templating import TemplateEngine

engine = TemplateEngine()
result = engine.render("Hello, {{ name }}!", name="World")

# From file
html = engine.render_file("templates/email.j2", context)
```

### Custom Filters

Add custom template filters:

```python
from codomyrmex.templating import TemplateEngine

engine = TemplateEngine()
engine.add_filter("capitalize_all", str.upper)
```

## PAI Integration Points

| Component | PAI Use Case |
|-----------|-------------|
| `TemplateEngine` | Render templates |
| `JinjaLoader` | Template loading |
| `Filters` | Custom filters |

## Navigation

- [README](README.md) | [AGENTS](AGENTS.md) | [SPEC](SPEC.md)
