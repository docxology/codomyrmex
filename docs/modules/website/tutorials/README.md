# Website Tutorials

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

Tutorials for generating websites and dashboards with Codomyrmex.

## Available Tutorials

| Tutorial | Description |
|----------|-------------|
| [Generate Site](#generate-site) | Generate static website |
| [Dashboard](#dashboard) | Create data dashboards |
| [Development Server](#development-server) | Run local dev server |

## Generate Site

```python
from codomyrmex.website import WebsiteGenerator

generator = WebsiteGenerator(
    template_dir="templates/",
    output_dir="dist/"
)

generator.build([
    ("index.html", "home.j2", {"title": "Home"}),
    ("about.html", "about.j2", {"title": "About"}),
])
```

## Dashboard

```python
from codomyrmex.website import DashboardBuilder

dashboard = DashboardBuilder()
dashboard.add_chart("users", chart_config)
dashboard.add_table("metrics", table_data)
dashboard.render("dashboard.html")
```

## Development Server

```python
from codomyrmex.website import WebsiteServer

server = WebsiteServer(port=8000)
server.serve("dist/")

# Open: http://localhost:8000
```

```bash
# Or via CLI
python -m codomyrmex.website serve dist/ --port 8000
```

## Navigation

- **Parent**: [Website Documentation](../README.md)
- **Source**: [src/codomyrmex/website/](../../../../src/codomyrmex/website/)
