# Agent Guidelines - Website

## Module Overview

Web dashboard, API server, and static site generator for the Codomyrmex ecosystem.

## Key Classes

- **WebsiteGenerator** — Renders Jinja2 templates into a static site
- **DataProvider** — Aggregates module, agent, script, config, and PAI data
- **WebsiteServer** — HTTP request handler with 18 REST API endpoints

## Agent Instructions

1. **Template-based** — All pages use Jinja2 templates in `templates/`
2. **Mobile-first** — Responsive design via CSS grid and media queries
3. **Fast loading** — Minimize external dependencies; Inter + Fira Code fonts only
4. **Accessible** — Skip links, ARIA labels, keyboard shortcuts (Alt+1–9)
5. **Secure** — Path traversal protection, origin validation, symlink blocking

## Common Patterns

```python
import socketserver
from codomyrmex.website import WebsiteGenerator, DataProvider, WebsiteServer

# Generate static website
generator = WebsiteGenerator(output_dir="./build", root_dir=".")
generator.generate()

# Start development server
WebsiteServer.root_dir = Path(".")
WebsiteServer.data_provider = DataProvider(Path("."))
with socketserver.TCPServer(("", 8787), WebsiteServer) as httpd:
    httpd.serve_forever()
```

## Testing Patterns

```python
# Verify generation (real templates, real DataProvider)
generator = WebsiteGenerator(output_dir=str(tmp_path / "out"), root_dir=str(tmp_path))
generator.generate()
assert (tmp_path / "out" / "index.html").exists()

# Verify data provider
provider = DataProvider(tmp_path)
modules = provider.get_modules()
assert isinstance(modules, list)
```

## Navigation

- [README](README.md) | [SPEC](SPEC.md) | [PAI](PAI.md)
