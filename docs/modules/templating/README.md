# Templating Documentation

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

Template engines: Jinja2, Mako, and custom templating.

## Key Features

- **Jinja2** — Full Jinja2 support
- **Mako** — Mako templates
- **Filters** — Custom filters
- **Macros** — Reusable components

## Quick Start

```python
from codomyrmex.templating import TemplateEngine

engine = TemplateEngine()
result = engine.render("Hello, {{ name }}!", name="World")

# From file
html = engine.render_file("templates/page.j2", data)
```

## Directory Contents

| File | Description |
|------|-------------|
| `README.md` | This file |
| `SPEC.md` | Technical specification |

## Navigation

- **Source**: [src/codomyrmex/templating/](../../../src/codomyrmex/templating/)
- **Parent**: [Modules](../README.md)
