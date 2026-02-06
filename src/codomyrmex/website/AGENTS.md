# Agent Guidelines - Website

## Module Overview

Web dashboard generation and static site building.

## Key Classes

- **WebsiteGenerator** — Generate static websites
- **DataProvider** — Data for dashboards
- **WebsiteServer** — Development server
- **PageBuilder** — Build individual pages

## Agent Instructions

1. **Template-based** — Use templates for consistency
2. **Mobile-first** — Responsive design
3. **Fast loading** — Optimize assets
4. **SEO ready** — Meta tags, sitemap
5. **Accessible** — WCAG compliance

## Common Patterns

```python
from codomyrmex.website import (
    WebsiteGenerator, DataProvider, WebsiteServer
)

# Generate website
generator = WebsiteGenerator(
    template_dir="templates/",
    output_dir="dist/"
)

# Add data
provider = DataProvider()
provider.add("metrics", get_metrics())
provider.add("modules", list_modules())

# Build pages
generator.build([
    ("index.html", "home.j2", provider.get("metrics")),
    ("modules.html", "list.j2", provider.get("modules")),
])

# Development server
server = WebsiteServer(port=8000)
server.serve("dist/")  # http://localhost:8000
```

## Testing Patterns

```python
# Verify generation
generator = WebsiteGenerator(output_dir="/tmp/site")
generator.build([("index.html", "base.j2", {})])
assert Path("/tmp/site/index.html").exists()

# Verify data provider
provider = DataProvider()
provider.add("key", [1, 2, 3])
assert provider.get("key") == [1, 2, 3]
```

## Navigation

- [README](README.md) | [SPEC](SPEC.md) | [PAI](PAI.md)
