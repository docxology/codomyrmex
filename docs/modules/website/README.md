# Website Documentation

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

Web dashboard generation and static site building.

## Key Features

- **Static Sites** — Generate HTML
- **Dashboards** — Data dashboards
- **Templates** — Jinja2 templates
- **Dev Server** — Local development

## Quick Start

```python
from codomyrmex.website import WebsiteGenerator, WebsiteServer

generator = WebsiteGenerator(output_dir="dist/")
generator.build([("index.html", "home.j2", data)])

server = WebsiteServer(port=8000)
server.serve("dist/")
```

## Directory Contents

| File | Description |
|------|-------------|
| `README.md` | This file |
| `SPEC.md` | Technical specification |

## Navigation

- **Source**: [src/codomyrmex/website/](../../../src/codomyrmex/website/)
- **Parent**: [Modules](../README.md)
